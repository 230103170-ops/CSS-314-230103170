import multiprocessing as mp
import time
import csv
import os
import statistics

ITERATIONS = 5_000_000
REPEATS = 3
PROCESS_COUNTS = [1, 2, 4, 8, 10]


def calculate_work(iterations):
    total = 0
    for i in range(iterations):
        total += (i % 100) * (i % 50)
    return total


def run_benchmark(processes):
    times = []

    for run in range(REPEATS):
        start = time.perf_counter()

        with mp.Pool(processes=processes) as pool:
            pool.map(calculate_work, [ITERATIONS] * processes)

        elapsed = time.perf_counter() - start
        times.append(elapsed)

        print(
            f"Processes: {processes:2d} | "
            f"Run: {run + 1} | "
            f"Time: {elapsed:.4f} seconds"
        )

    return statistics.mean(times)


if __name__ == "__main__":
    print("APPLE M4 WEAK SCALING BENCHMARK")
    print("CPU cores:", os.cpu_count())
    print("Iterations per process:", ITERATIONS)
    print("Runs per configuration:", REPEATS)
    print("-" * 55)

    results = []

    for processes in PROCESS_COUNTS:
        average_time = run_benchmark(processes)
        results.append({
            "processes": processes,
            "iterations_per_process": ITERATIONS,
            "average_time": average_time
        })

    with open("benchmarks/weak_scale_bench/results.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print("\nRESULTS")
    for result in results:
        print(
            f"{result['processes']:2d} processes: "
            f"{result['average_time']:.4f} seconds"
        )

    print("\nResults saved to benchmarks/weak_scale_bench/results.csv")
