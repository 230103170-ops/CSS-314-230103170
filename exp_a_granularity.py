import json
import multiprocessing as mp
import statistics
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "variant_b_results"


def collatz_steps(n):
    steps = 0
    while n > 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


def run_granularity(workers, total_items=1_000_000, chunk_size=1):
    numbers = range(1, total_items + 1)

    start = time.perf_counter()
    with mp.Pool(processes=workers) as pool:
        results = pool.map(
            collatz_steps, numbers, chunksize=chunk_size
        )
    elapsed = time.perf_counter() - start

    return elapsed, sum(results)


def main():
    OUTPUT.mkdir(exist_ok=True)
    rows = []

    print("Calculating sequential reference checksum...", flush=True)
    reference = sum(collatz_steps(n) for n in range(1, 1_000_001))
    print(f"Reference checksum: {reference}", flush=True)

    for chunk_size in [1, 10_000]:
        for p in [1, 2, 4, 8]:
            times = []

            for run in range(1, 4):
                print(
                    f"Starting: chunk={chunk_size}, "
                    f"P={p}, run={run}/3",
                    flush=True,
                )

                elapsed, checksum = run_granularity(
                    p, chunk_size=chunk_size
                )
                if checksum != reference:
                    raise RuntimeError(
                        f"Checksum mismatch: {checksum} != {reference}"
                    )

                times.append(elapsed)
                print(
                    f"Time={elapsed:.4f}s | checksum={checksum} | PASS",
                    flush=True,
                )

            rows.append({
                "chunk_size": chunk_size,
                "p": p,
                "total_items": 1_000_000,
                "times_seconds": times,
                "median_seconds": statistics.median(times),
                "checksum": checksum,
                "reference_checksum": reference,
            })

            (OUTPUT / "A_raw.json").write_text(
                json.dumps(rows, indent=2) + "\n",
                encoding="utf-8",
            )

    for chunk_size in [1, 10_000]:
        group = [r for r in rows if r["chunk_size"] == chunk_size]
        t1 = next(r["median_seconds"] for r in group if r["p"] == 1)

        print(f"\nSUMMARY: chunksize={chunk_size}")
        for row in group:
            p = row["p"]
            tp = row["median_seconds"]
            row["speedup"] = t1 / tp
            row["efficiency_percent"] = 100 * t1 / (p * tp)
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
        "experiment": "A: Task granularity",
        "start_method": mp.get_context().get_start_method(),
        "repeats": 3,
        "timing_scope": (
            "Pool startup, map and shutdown; "
            "reference calculation and checksum reduction excluded."
        ),
        "rows": rows,
    }

    (OUTPUT / "A.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\nCoarse versus fine at the same worker count:")
    for p in [1, 2, 4, 8]:
        fine = next(
            r["median_seconds"] for r in rows
            if r["p"] == p and r["chunk_size"] == 1
        )
        coarse = next(
            r["median_seconds"] for r in rows
            if r["p"] == p and r["chunk_size"] == 10_000
        )
        print(f"P={p}: T_fine/T_coarse = {fine / coarse:.3f}x")

    print("\nAll checksum checks: PASS")
    print("Saved: variant_b_results/A.json")


if __name__ == "__main__":
    mp.freeze_support()
    main()
