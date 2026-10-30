import math
import multiprocessing as mp
import time

from practice_common import benchmark


def heavy_math(n):
    return sum(
        math.sin(i) * math.cos(i)
        for i in range(1, n)
    )


def run_experiment(workers, total_chunks=16, chunk_size=2_000_000):
    start = time.perf_counter()
    time.sleep(0.40)

    with mp.Pool(processes=workers) as pool:
        values = pool.map(
            heavy_math,
            [chunk_size] * total_chunks,
        )

    elapsed = time.perf_counter() - start

    if len(values) != total_chunks:
        raise RuntimeError("Missing chunk results")
    if not all(math.isfinite(v) for v in values):
        raise RuntimeError("Non-finite result")
    if not all(v == values[0] for v in values):
        raise RuntimeError("Identical chunks returned different results")

    return elapsed


if __name__ == "__main__":
    mp.freeze_support()
    benchmark(
        "A",
        run_experiment,
        {
            "total_chunks": 16,
            "chunk_size": 2_000_000,
            "serial_sleep_seconds": 0.40,
        },
    )
