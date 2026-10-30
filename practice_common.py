import json
import multiprocessing as mp
import os
import platform
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "practice_results"


def sysctl(key):
    result = subprocess.run(
        ["sysctl", "-n", key],
        capture_output=True, text=True,
    )
    value = result.stdout.strip()
    if result.returncode != 0 or not value:
        return None
    try:
        return int(value)
    except ValueError:
        return value


def benchmark(name, run_experiment, parameters):
    DATA.mkdir(exist_ok=True)
    rows = []

    for p in [1, 2, 4]:
        times = []
        for run in range(1, 4):
            elapsed = run_experiment(p)
            times.append(elapsed)
            print(
                f"{name}: P={p} run={run}/3 "
                f"time={elapsed:.4f}s",
                flush=True,
            )
        rows.append({
            "p": p,
            "times_seconds": times,
            "median_seconds": statistics.median(times),
        })

    t1 = rows[0]["median_seconds"]
    for row in rows:
        p = row["p"]
        tp = row["median_seconds"]
        row["speedup"] = t1 / tp
        row["efficiency_percent"] = 100 * t1 / (p * tp)
        row["karp_flatt"] = (
            ((p * tp / t1) - 1) / (p - 1)
            if p > 1 else None
        )

    report = {
        "experiment": name,
        "parameters": parameters,
        "timing": "End-to-end, including process startup and shutdown",
        "start_method": mp.get_context().get_start_method(),
        "rows": rows,
    }
    (DATA / f"{name}.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    hardware = {
        "cpu_model": sysctl("machdep.cpu.brand_string"),
        "physical_cores": sysctl("hw.physicalcpu"),
        "logical_cores": os.cpu_count(),
        "cache_line_bytes": sysctl("hw.cachelinesize"),
        "architecture": platform.machine(),
        "os": platform.platform(),
        "python": platform.python_version(),
    }
    (DATA / "hardware.json").write_text(
        json.dumps(hardware, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"\n{name} SUMMARY")
    for row in rows:
        e = row["karp_flatt"]
        e_text = "-" if e is None else f"{e:.4f}"
        print(
            f"P={row['p']} "
            f"T={row['median_seconds']:.4f}s "
            f"S={row['speedup']:.3f}x "
            f"E={row['efficiency_percent']:.1f}% "
            f"e={e_text}"
        )
    print(f"Saved: practice_results/{name}.json")
