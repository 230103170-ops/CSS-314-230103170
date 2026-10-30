import csv
import json
import statistics
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"


def traverse(data, stride):
    total = 0.0
    for i in range(0, data.size, stride):
        total += data[i]
    return total


def main():
    params = json.loads(
        (RESULTS / "salted_params.json").read_text()
    )
    size = params["buffer_elements"]
    data = np.ones(size, dtype=np.float64)

    output = RESULTS / "stride_results.tsv"

    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow([
            "stride",
            "step_bytes",
            "elements_touched",
            "run",
            "elapsed_ns",
            "ns_per_element",
            "median_time_ns",
            "median_ns_per_element",
            "checksum",
        ])

        for stride in [1, 2, 4, 8, 16, 32, 64, 128]:
            touched = len(range(0, size, stride))
            print(f"Stride {stride}: warmup...", flush=True)

            for _ in range(5):
                total = traverse(data, stride)
                if total != touched:
                    raise RuntimeError("Warmup checksum mismatch")

            times = []
            totals = []

            for run in range(1, 6):
                start = time.perf_counter_ns()
                total = traverse(data, stride)
                elapsed = time.perf_counter_ns() - start

                if total != touched:
                    raise RuntimeError("Measurement checksum mismatch")

                times.append(elapsed)
                totals.append(total)
                print(
                    f"  Run {run}/5: {elapsed / 1e9:.4f} s",
                    flush=True,
                )

            median_ns = statistics.median(times)

            for run, (elapsed, total) in enumerate(
                zip(times, totals), start=1
            ):
                writer.writerow([
                    stride,
                    stride * data.itemsize,
                    touched,
                    run,
                    elapsed,
                    elapsed / touched,
                    median_ns,
                    median_ns / touched,
                    total,
                ])

            file.flush()
            print(
                f"Stride {stride}: median "
                f"{median_ns / touched:.2f} ns/element",
                flush=True,
            )

    print(f"\nSaved: {output}")


if __name__ == "__main__":
    main()
