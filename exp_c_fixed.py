import multiprocessing as mp
import time

from practice_common import benchmark


def private_worker(iterations):
    local_sum = 0
    for _ in range(iterations):
        local_sum += 1
    return local_sum


def run_privatized(p, total_increments=20_000_000):
    base, remainder = divmod(total_increments, p)
    tasks = [base + (i < remainder) for i in range(p)]

    start = time.perf_counter()

    with mp.Pool(processes=p) as pool:
        values = pool.map(private_worker, tasks)

    total = sum(values)
    elapsed = time.perf_counter() - start

    if values != tasks or total != total_increments:
        raise RuntimeError("Privatized counter verification failed")

    return elapsed


if __name__ == "__main__":
    mp.freeze_support()
    benchmark(
        "C",
        run_privatized,
        {"total_increments": 20_000_000},
    )
