import json
import multiprocessing as mp
import statistics
import time
from pathlib import Path
from queue import Empty


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "variant_b_results"


def queue_worker(out_queue, items_per_worker):
    for i in range(items_per_worker):
        out_queue.put(i % 7)


def expected_sum(count):
    full, remainder = divmod(count, 7)
    return full * 21 + remainder * (remainder - 1) // 2


def run_queue_benchmark(p, total_items=400_000):
    q = mp.Queue()
    base, remainder = divmod(total_items, p)
    counts = [base + (i < remainder) for i in range(p)]

    workers = [
        mp.Process(target=queue_worker, args=(q, count))
        for count in counts
    ]

    started = []
    total_sum = 0
    start = time.perf_counter()

    try:
        for worker in workers:
            worker.start()
            started.append(worker)

        for _ in range(total_items):
            try:
                total_sum += q.get(timeout=60)
            except Empty as error:
                raise RuntimeError(
                    "No queue data for 60 seconds; benchmark stopped."
                ) from error

        for worker in workers:
            worker.join(timeout=60)
            if worker.is_alive() or worker.exitcode != 0:
                raise RuntimeError("Worker did not finish successfully")

        elapsed = time.perf_counter() - start

    finally:
        for worker in started:
            if worker.is_alive():
                worker.terminate()
            worker.join()
        q.close()
        q.join_thread()

    expected = sum(expected_sum(count) for count in counts)
    if total_sum != expected:
        raise RuntimeError(
            f"Checksum mismatch: {total_sum} != {expected}"
        )

    return elapsed, total_sum, expected


def main():
    OUTPUT.mkdir(exist_ok=True)
    rows = []

    for p in [1, 2, 4, 8]:
        times = []

        for run in range(1, 4):
            print(f"Starting P={p}, run={run}/3...", flush=True)
            elapsed, checksum, expected = run_queue_benchmark(p)
            times.append(elapsed)

            print(
                f"P={p} | time={elapsed:.4f}s | "
                f"checksum={checksum} | PASS",
                flush=True,
            )

        rows.append({
            "p": p,
            "total_items": 400_000,
            "times_seconds": times,
            "median_seconds": statistics.median(times),
            "checksum": checksum,
            "expected_checksum": expected,
        })

        (OUTPUT / "B_raw.json").write_text(
            json.dumps(rows, indent=2) + "\n",
            encoding="utf-8",
        )

    t1 = rows[0]["median_seconds"]

    print("\nSUMMARY: Queue contention")
    for row in rows:
        p = row["p"]
        tp = row["median_seconds"]

        row["speedup"] = t1 / tp
        row["efficiency_percent"] = 100 * t1 / (p * tp)
        row["throughput_items_per_second"] = 400_000 / tp
        row["karp_flatt"] = (
            ((p * tp / t1) - 1) / (p - 1)
            if p > 1 else None
        )

        e = row["karp_flatt"]
        e_text = "-" if e is None else f"{e:.4f}"

        print(
            f"P={p} | T={tp:.4f}s | "
            f"S={row['speedup']:.3f}x | "
            f"E={row['efficiency_percent']:.2f}% | e={e_text}"
        )

    report = {
        "student_id": "230103170",
        "experiment": "B: Unbuffered queue",
        "start_method": mp.get_context().get_start_method(),
        "repeats": 3,
        "timing_scope": (
            "Process startup, queue puts/gets, consumer checksum "
            "accumulation and worker joins; queue cleanup excluded."
        ),
        "notes": (
            "Each worker starts its own i % 7 sequence, as in the handout. "
            "Expected checksum is calculated for each partition."
        ),
        "rows": rows,
    }

    (OUTPUT / "B.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\nAll checksum checks: PASS")
    print("Saved: variant_b_results/B.json")


if __name__ == "__main__":
    mp.freeze_support()
    main()
