import json
import statistics
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"


def multiply_ijk(a, b, m):
    c = np.zeros((m, m), dtype=np.float64)
    for i in range(m):
        for j in range(m):
            total = 0.0
            for k in range(m):
                total += a[i, k] * b[k, j]
            c[i, j] = total
    return c


def multiply_ikj(a, b, m):
    c = np.zeros((m, m), dtype=np.float64)
    for i in range(m):
        for k in range(m):
            aik = a[i, k]
            for j in range(m):
                c[i, j] += aik * b[k, j]
    return c


def main():
    params = json.loads(
        (RESULTS / "salted_params.json").read_text()
    )
    n = params["N"]
    m = n // 2

    rng = np.random.default_rng(params["seed"])
    a = rng.random((n, n))
    b = rng.random((n, n))

    print(f"N = {n}, measured block M = {m}", flush=True)
    print("Checking both algorithms on a small block...", flush=True)

    small_m = 16
    small_ref = a[:small_m, :small_m] @ b[:small_m, :small_m]
    for kernel in (multiply_ijk, multiply_ikj):
        np.testing.assert_allclose(
            kernel(a, b, small_m),
            small_ref,
            rtol=0,
            atol=1e-12,
        )

    times = {"ijk": [], "ikj": []}
    outputs = {}
    kernels = {"ijk": multiply_ijk, "ikj": multiply_ikj}

    for run in range(1, 4):
        order = ("ijk", "ikj") if run % 2 else ("ikj", "ijk")

        for name in order:
            print(f"{name}: run {run}/3 started...", flush=True)
            start = time.perf_counter_ns()
            result = kernels[name](a, b, m)
            elapsed = time.perf_counter_ns() - start

            if name in outputs:
                np.testing.assert_array_equal(result, outputs[name])

            outputs[name] = result
            times[name].append(elapsed)

            print(
                f"{name}: run {run}/3 = {elapsed / 1e9:.3f} s",
                flush=True,
            )

    np.testing.assert_allclose(
        outputs["ijk"], outputs["ikj"],
        rtol=0, atol=1e-12,
    )

    reference = a[:m, :m] @ b[:m, :m]
    for result in outputs.values():
        np.testing.assert_allclose(
            result, reference, rtol=0, atol=1e-12,
        )

    median_ijk = statistics.median(times["ijk"])
    median_ikj = statistics.median(times["ikj"])
    max_error = float(
        np.max(np.abs(outputs["ijk"] - outputs["ikj"]))
    )

    report = {
        "student_id": params["student_id"],
        "N": n,
        "M": m,
        "seed": params["seed"],
        "implementation": "CPython explicit loops with NumPy arrays",
        "input_layout": "C-contiguous N x N arrays; top-left M x M block",
        "runs_per_algorithm": 3,
        "timing_scope": "output allocation and multiplication",
        "ijk_times_ns": times["ijk"],
        "ikj_times_ns": times["ikj"],
        "ijk_median_seconds": median_ijk / 1e9,
        "ikj_median_seconds": median_ikj / 1e9,
        "speedup_ijk_over_ikj": median_ijk / median_ikj,
        "max_absolute_difference": max_error,
        "absolute_tolerance": 1e-12,
        "verification_passed": True,
    }

    np.save(RESULTS / "dense_ijk.npy", outputs["ijk"])
    np.save(RESULTS / "dense_ikj.npy", outputs["ikj"])
    np.save(RESULTS / "dense_reference.npy", reference)

    output = RESULTS / "loop_interchange.json"
    output.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\nNumerical verification: PASS")
    print(json.dumps(report, indent=2))
    print(f"\nSaved: {output}")


if __name__ == "__main__":
    main()
