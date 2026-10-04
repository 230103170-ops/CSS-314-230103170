import time
import multiprocessing as mp

WORK = 20_000_000
WORKERS = [1, 2, 4, 8, 16, 32]
RUNS = 3

def compute(start, end):
    total = 0
    for i in range(start, end):
        total += (i % 97) * (i % 89)
    return total

def benchmark(workers):
    chunk = WORK // workers
    ranges = []

    for w in range(workers):
        start = w * chunk
        end = WORK if w == workers - 1 else (w + 1) * chunk
        ranges.append((start, end))

    start_time = time.perf_counter()

    with mp.Pool(processes=workers) as pool:
        pool.starmap(compute, ranges)

    return time.perf_counter() - start_time

if __name__ == "__main__":
    print("Task 2 - Multi-Thread Scaling Benchmark")
    print(f"Total workload: {WORK:,}")
    print()

    results = {}

    for workers in WORKERS:
        times = []

        for run in range(RUNS):
            t = benchmark(workers)
            times.append(t)
            print(f"{workers:2d} workers | Run {run + 1}: {t:.4f} s")

        avg = sum(times) / RUNS
        results[workers] = (times, avg)
        print(f"   Average: {avg:.4f} s\n")

    baseline = results[1][1]

    print("=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print("Workers | Avg Time (s) | Speedup | Efficiency")
    
    for workers in WORKERS:
        avg = results[workers][1]
        speedup = baseline / avg
        efficiency = speedup / workers * 100
        print(
            f"{workers:7d} | {avg:12.4f} | "
            f"{speedup:7.2f}x | {efficiency:9.2f}%"
        )
