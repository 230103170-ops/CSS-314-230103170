import csv
import ctypes
import json
import multiprocessing as mp
import statistics
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
ITERATIONS = 5_000_000
REPEATS = 3


def worker(shared, index, iterations, mode, barrier):
    barrier.wait(timeout=120)

    if mode == "privatized":
        local = 0
        for _ in range(iterations):
            local += 1
        shared[index] = local
    else:
        for _ in range(iterations):
            shared[index] += 1


def measure(ctx, processes, spacing, mode, line_bytes):
    item_bytes = ctypes.sizeof(ctypes.c_int64)
    alignment_items = line_bytes // item_bytes

    shared = ctx.RawArray(
        ctypes.c_int64,
        processes * spacing + alignment_items,
    )

    address = ctypes.addressof(shared)
    offset_bytes = (-address) % line_bytes
    if offset_bytes % item_bytes:
        raise RuntimeError("Cannot align shared counters")

    offset = offset_bytes // item_bytes
    indices = [offset + p * spacing for p in range(processes)]
    barrier = ctx.Barrier(processes + 1)

    children = [
        ctx.Process(
            target=worker,
            args=(shared, index, ITERATIONS, mode, barrier),
        )
        for index in indices
    ]

    started = []
    try:
        for child in children:
            child.start()
            started.append(child)

        # Wait until all workers have been started.
        # Timing includes the start barrier and process completion.
        start = time.perf_counter_ns()
        barrier.wait(timeout=120)

        for child in children:
            child.join()
            if child.exitcode != 0:
                raise RuntimeError(
                    f"Worker failed: exit code {child.exitcode}"
                )

        elapsed_ns = time.perf_counter_ns() - start
    finally:
        for child in started:
            if child.is_alive():
                child.terminate()
            child.join()

    counts = [int(shared[index]) for index in indices]
    if counts != [ITERATIONS] * processes:
        raise RuntimeError(f"Incorrect counters: {counts}")

    return elapsed_ns, counts


def main():
    profile = json.loads(
        (RESULTS / "host_profile.json").read_text()
    )
    line_bytes = int(profile["cache_line_bytes"])
    item_bytes = ctypes.sizeof(ctypes.c_int64)

    if line_bytes % item_bytes:
        raise ValueError("Unexpected cache-line size")

    ctx = mp.get_context("spawn")
    variants = {
        "unpadded": 1,
        "padded_64": 64 // item_bytes,
        "padded_native": line_bytes // item_bytes,
        "privatized": 1,
    }

    rows = []
    medians = {}

    print(f"Cache line: {line_bytes} bytes", flush=True)
    print(f"Iterations per worker: {ITERATIONS}", flush=True)

    for mode, spacing in variants.items():
        for processes in [1, 2, 4, 8]:
            measurements = []

            for run in range(1, REPEATS + 1):
                elapsed_ns, counts = measure(
                    ctx, processes, spacing, mode, line_bytes
                )
                measurements.append(elapsed_ns)

                rows.append({
                    "variant": mode,
                    "processes": processes,
                    "run": run,
                    "iterations_per_worker": ITERATIONS,
                    "spacing_bytes": spacing * item_bytes,
                    "elapsed_ns": elapsed_ns,
                    "total_count": sum(counts),
                    "expected_total": processes * ITERATIONS,
                    "counts_json": json.dumps(counts),
                })

                print(
                    f"{mode:15s} P={processes} "
                    f"run={run}/{REPEATS} "
                    f"time={elapsed_ns / 1e9:.4f}s "
                    f"count={sum(counts)} PASS",
                    flush=True,
                )

            medians[(mode, processes)] = statistics.median(
                measurements
            )

            # Save completed runs, even if a later run is interrupted.
            (RESULTS / "false_sharing_raw.json").write_text(
                json.dumps(rows, indent=2) + "\n",
                encoding="utf-8",
            )

    for row in rows:
        mode = row["variant"]
        p = row["processes"]
        t1 = medians[(mode, 1)]
        tp = medians[(mode, p)]
        time_ratio = t1 / tp

        row["median_time_ns"] = tp
        row["T1_over_TP"] = time_ratio
        row["throughput_speedup"] = p * time_ratio
        row["weak_efficiency"] = time_ratio

        # Literal assignment formula. Work grows with P,
        # so this is NOT a strong-scaling serial fraction.
        row["karp_flatt_assignment"] = (
            ((1 / time_ratio) - (1 / p)) / (1 - (1 / p))
            if p > 1 else ""
        )

    output = RESULTS / "false_sharing_karp_flatt.tsv"
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0]),
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(rows)

    metadata = {
        "cache_line_bytes": line_bytes,
        "start_method": "spawn",
        "repeats": REPEATS,
        "iterations_per_worker": ITERATIONS,
        "shared_array": "RawArray without a global lock",
        "base_alignment_bytes": line_bytes,
        "timing_scope": (
            "Parent start-barrier wait through worker joins; "
            "includes remaining worker startup and shutdown overhead."
        ),
        "metric_note": (
            "Each worker performs K iterations, so total work is P*K. "
            "T1/TP is weak-scaling efficiency; throughput speedup is "
            "P*T1/TP. The assignment Karp-Flatt formula is recorded "
            "literally but is not a strong-scaling serial fraction here."
        ),
    }
    (RESULTS / "false_sharing_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\nMedian times (seconds):")
    for mode in variants:
        values = [
            f"P={p}: {medians[(mode, p)] / 1e9:.4f}"
            for p in [1, 2, 4, 8]
        ]
        print(f"{mode}: " + ", ".join(values))

    print("\nAll counter checks: PASS")
    print(f"Saved: {output}")


if __name__ == "__main__":
    mp.freeze_support()
    main()
