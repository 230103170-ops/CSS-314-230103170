import csv
import ctypes
import hashlib
import json
import math
import multiprocessing as mp
import statistics
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
STEPS = 20
REPEATS = 3
BUFFERS = None


def initialize(raw_a, raw_b, n):
    global BUFFERS
    BUFFERS = (
        np.frombuffer(raw_a, dtype=np.float64).reshape(n, n),
        np.frombuffer(raw_b, dtype=np.float64).reshape(n, n),
    )


def update_rows(source, target, lo, hi):
    target[lo:hi, 1:-1] = (
        source[lo:hi, 1:-1]
        + source[lo-1:hi-1, 1:-1]
        + source[lo+1:hi+1, 1:-1]
        + source[lo:hi, :-2]
        + source[lo:hi, 2:]
    ) * 0.2


def worker(task):
    parity, lo, hi = task
    update_rows(BUFFERS[parity], BUFFERS[1-parity], lo, hi)


def reference(initial):
    a = initial.copy()
    b = np.zeros_like(a)
    for _ in range(STEPS):
        update_rows(a, b, 1, a.shape[0] - 1)
        a, b = b, a
    return a


def digest(array, student_id):
    h = hashlib.sha256(student_id.encode("utf-8"))
    values = np.ascontiguousarray(
        np.round(array, 6), dtype="<f8"
    )
    h.update(values.tobytes())
    return h.hexdigest()


def measure(ctx, initial, processes):
    n = initial.shape[0]
    raw_a = ctx.RawArray(ctypes.c_double, n * n)
    raw_b = ctx.RawArray(ctypes.c_double, n * n)

    a = np.frombuffer(raw_a, dtype=np.float64).reshape(n, n)
    b = np.frombuffer(raw_b, dtype=np.float64).reshape(n, n)
    a[:] = initial
    b.fill(0)

    edges = np.linspace(1, n - 1, processes + 1, dtype=int)
    chunks = [
        (int(edges[i]), int(edges[i+1]))
        for i in range(processes)
    ]

    start = time.perf_counter_ns()

    with ctx.Pool(
        processes,
        initializer=initialize,
        initargs=(raw_a, raw_b, n),
    ) as pool:
        for step in range(STEPS):
            pool.map(
                worker,
                [(step % 2, lo, hi) for lo, hi in chunks],
            )

    elapsed = time.perf_counter_ns() - start
    output = a if STEPS % 2 == 0 else b
    return elapsed, output.copy()


def main():
    params = json.loads(
        (RESULTS / "salted_params.json").read_text()
    )
    profile = json.loads(
        (RESULTS / "host_profile.json").read_text()
    )

    n = params["N"]
    cores = int(profile["physical_cores"])
    workers = []
    p = 1
    while p <= cores:
        workers.append(p)
        p *= 2
    if cores not in workers:
        workers.append(cores)

    ctx = mp.get_context("spawn")
    rows = []

    for study in ("strong", "weak"):
        for p in workers:
            dim = n if study == "strong" else math.ceil(n * math.sqrt(p))
            rng = np.random.default_rng(params["seed"])
            initial = rng.random((dim, dim))
            initial[0, :] = 0
            initial[-1, :] = 0
            initial[:, 0] = 0
            initial[:, -1] = 0

            expected = reference(initial)
            expected_hash = digest(expected, params["student_id"])
            times = []
            max_error = 0.0

            for run in range(1, REPEATS + 1):
                elapsed, actual = measure(ctx, initial, p)

                np.testing.assert_allclose(
                    actual, expected, rtol=0, atol=1e-12
                )
                actual_hash = digest(actual, params["student_id"])
                if actual_hash != expected_hash:
                    raise RuntimeError("Rounded digest mismatch")

                max_error = max(
                    max_error,
                    float(np.max(np.abs(actual - expected))),
                )
                times.append(elapsed)

                print(
                    f"{study:6s} P={p:2d} N={dim} "
                    f"run={run}/{REPEATS}: "
                    f"{elapsed / 1e9:.4f}s PASS",
                    flush=True,
                )

            median_s = statistics.median(times) / 1e9
            updates = STEPS * (dim - 2) ** 2
            rows.append({
                "study": study,
                "processes": p,
                "N": dim,
                "steps": STEPS,
                "cell_updates": updates,
                "times_ns_json": json.dumps(times),
                "median_seconds": median_s,
                "gflops_per_second": 5 * updates / median_s / 1e9,
                "max_absolute_error": max_error,
                "reference_digest": expected_hash,
                "output_digest": actual_hash,
                "verified": True,
            })

            (RESULTS / "scaling_raw.json").write_text(
                json.dumps(rows, indent=2) + "\n",
                encoding="utf-8",
            )

    baselines = {
        study: next(
            row for row in rows
            if row["study"] == study and row["processes"] == 1
        )
        for study in ("strong", "weak")
    }

    for row in rows:
        base = baselines[row["study"]]
        p = row["processes"]
        ratio = base["median_seconds"] / row["median_seconds"]
        work_ratio = row["cell_updates"] / base["cell_updates"]

        row["T1_over_TP"] = ratio
        row["strong_speedup"] = ratio if row["study"] == "strong" else ""
        row["strong_efficiency_percent"] = (
            100 * ratio / p if row["study"] == "strong" else ""
        )
        row["weak_efficiency_percent"] = (
            100 * ratio if row["study"] == "weak" else ""
        )
        row["throughput_speedup"] = work_ratio * ratio
        row["scaled_speedup_pdf_formula"] = (
            p * ratio / work_ratio if row["study"] == "weak" else ""
        )
        row["effective_serial_fraction"] = (
            (1 / ratio - 1 / p) / (1 - 1 / p)
            if row["study"] == "strong" and p > 1 else ""
        )

    strong = [r for r in rows if r["study"] == "strong"]
    t1 = baselines["strong"]["median_seconds"]
    x = np.array([1 - 1 / r["processes"] for r in strong])
    y = np.array([
        r["median_seconds"] / t1 - 1 / r["processes"]
        for r in strong
    ])
    s = float(np.dot(x, y) / np.dot(x, x)) if np.dot(x, x) else None
    valid = s is not None and 0 <= s <= 1

    model = {
        "timing_scope": (
            "Pool startup, 20 stencil steps, dispatch, synchronization, "
            "and pool shutdown. Input allocation and verification excluded."
        ),
        "amdahl_fit_method": "Least squares on TP/T1 = s + (1-s)/P",
        "amdahl_serial_fraction_unconstrained": s,
        "amdahl_fraction_in_physical_range": valid,
        "amdahl_asymptotic_speedup": (
            1 / s if valid and s > 0 else None
        ),
        "gustafson_predictions": (
            {str(p): p - s * (p - 1) for p in workers}
            if valid else None
        ),
        "notes": [
            "If s is outside [0,1], the simple Amdahl model is inadequate.",
            "Startup overhead and heterogeneous cores affect scaling.",
            "The PDF weak-scaling formula is recorded literally.",
            "Measured throughput speedup uses actual cell-update counts.",
            "Gustafson predictions use the fitted strong-scaling fraction "
            "as an illustrative assumption, not a measured weak serial fraction.",
        ],
    }

    roofline = {
        "kernel": "Five-point average, float64, zero fixed boundaries",
        "flops_per_cell_update": 5,
        "source_level_bytes_per_update": 48,
        "source_level_arithmetic_intensity_flops_per_byte": 5 / 48,
        "ideal_reuse_bytes_per_update": 16,
        "ideal_reuse_arithmetic_intensity_flops_per_byte": 5 / 16,
        "peak_memory_bandwidth_GB_s": None,
        "peak_compute_GFLOPS_s": None,
        "classification": "Inconclusive from available measurements",
        "interpretation": (
            "The stencil has low arithmetic intensity and may be "
            "memory-bandwidth limited at native-kernel level. "
            "These end-to-end Python timings also include process and "
            "synchronization overhead; they do not establish a DRAM bottleneck."
        ),
        "traffic_notes": (
            "48 bytes counts five loads and one store at source level. "
            "16 bytes assumes ideal spatial reuse with one input read "
            "and one output write. Neither is measured DRAM traffic; "
            "NumPy temporaries, write allocation and cache reuse alter traffic."
        ),
        "base_grid_bytes": n * n * 8,
        "base_two_grid_bytes": 2 * n * n * 8,
        "cache_line_bytes": profile["cache_line_bytes"],
        "performance_levels": profile["performance_levels"],
        "best_measured_end_to_end_GFLOPS_s": max(
            r["gflops_per_second"] for r in rows
        ),
    }

    with (RESULTS / "scaling_metrics.tsv").open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=list(rows[0]), delimiter="\t"
        )
        writer.writeheader()
        writer.writerows(rows)

    for name, data in (
        ("scaling_models.json", model),
        ("roofline_summary.json", roofline),
    ):
        (RESULTS / name).write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )

    print("\nSUMMARY")
    for row in rows:
        print(
            f"{row['study']:6s} P={row['processes']:2d} "
            f"T={row['median_seconds']:.4f}s "
            f"T1/TP={row['T1_over_TP']:.3f} "
            f"throughput={row['throughput_speedup']:.3f}x"
        )

    print(f"\nAmdahl fitted s: {s}")
    print(f"Amdahl physical range: {valid}")
    print("All stencil checks: PASS")
    print("Saved: results/scaling_metrics.tsv")
    print("Saved: results/roofline_summary.json")


if __name__ == "__main__":
    mp.freeze_support()
    main()
