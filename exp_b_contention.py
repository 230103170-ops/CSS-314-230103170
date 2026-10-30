import multiprocessing as mp
import time

from practice_common import benchmark


def contended_worker(counter, lock, iterations):
    for _ in range(iterations):
        with lock:
            counter.value += 1


def run_contended(p, total_increments=2_000_000):
    counter = mp.Value("i", 0)
    lock = mp.Lock()
    base, remainder = divmod(total_increments, p)

    processes = [
        mp.Process(
            target=contended_worker,
            args=(counter, lock, base + (i < remainder)),
        )
        for i in range(p)
    ]

    start = time.perf_counter()
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    elapsed = time.perf_counter() - start

    for process in processes:
        if process.exitcode != 0:
            raise RuntimeError(
                f"Worker failed: {process.exitcode}"
            )

    if counter.value != total_increments:
        raise RuntimeError(
            f"Count mismatch: {counter.value} != {total_increments}"
        )

    return elapsed


if __name__ == "__main__":
    mp.freeze_support()
    benchmark(
        "B",
        run_contended,
        {"total_increments": 2_000_000},
    )
