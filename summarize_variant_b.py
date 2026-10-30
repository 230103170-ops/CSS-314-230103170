import json
import platform
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "variant_b_results"


def read(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def sysctl(key):
    result = subprocess.run(
        ["sysctl", "-n", key],
        capture_output=True, text=True,
    )
    return result.stdout.strip() or "Unavailable"


a = read("A.json")["rows"]
b = read("B.json")["rows"]
c = read("C.json")["rows"]

groups = {
    "A: Micro (k=1)": {r["p"]: r for r in a if r["chunk_size"] == 1},
    "A: Coarse (k=10000)": {
        r["p"]: r for r in a if r["chunk_size"] == 10_000
    },
    "B: Queue": {r["p"]: r for r in b},
    "C: Buffered": {r["p"]: r for r in c},
}

fine = groups["A: Micro (k=1)"]
coarse = groups["A: Coarse (k=10000)"]
queue = groups["B: Queue"]
buffered = groups["C: Buffered"]

b_negative = queue[8]["median_seconds"] > queue[1]["median_seconds"]
b_monotonic = (
    queue[2]["karp_flatt"]
    < queue[4]["karp_flatt"]
    < queue[8]["karp_flatt"]
)
c_speedup = buffered[8]["speedup"]
c_e8 = buffered[8]["karp_flatt"]

lines = [
    "# Scalability Diagnostics — Variant B",
    "",
    "Symbat Aldanova — 230103170",
    "",
    "## Hardware and method",
    "",
    f"- CPU: {sysctl('machdep.cpu.brand_string')}",
    f"- Physical cores: {sysctl('hw.physicalcpu')}",
    f"- Logical cores: {sysctl('hw.logicalcpu')}",
    f"- Cache-line size: {sysctl('hw.cachelinesize')} bytes",
    f"- OS: {platform.platform()}",
    f"- Python: {platform.python_version()}",
    f"- Process start method: {read('C.json')['start_method']}",
    "- Three measurements per configuration; reported times are medians.",
    "- Timings include process startup, communication and shutdown.",
    "- A: 1,000,000 Collatz inputs; chunksize 1 versus 10,000.",
    "- B: 400,000 records sent individually through a shared queue.",
    "- C: 10,000,000 records, locally aggregated in batches of 10,000.",
    "- B and C restart the i % 7 sequence in each worker, following the handout.",
    "- Checksums are validated against each configuration's expected result.",
    "- Total work is fixed across process counts within each experiment.",
    "",
    "## Measurements",
    "",
    "| Configuration | T1 (s) | T2 (s) | T4 (s) | T8 (s) | S8 | e(2) | e(8) |",
    "|---|---:|---:|---:|---:|---:|---:|---:|",
]

for name, group in groups.items():
    times = " | ".join(
        f"{group[p]['median_seconds']:.6f}" for p in (1, 2, 4, 8)
    )
    lines.append(
        f"| {name} | {times} "
        f"| {group[8]['speedup']:.4f} "
        f"| {group[2]['karp_flatt']:.4f} "
        f"| {group[8]['karp_flatt']:.4f} |"
    )

lines += [
    "",
    "## Detailed scaling",
    "",
    "| Configuration | P | Speedup | Efficiency (%) | e(p) |",
    "|---|---:|---:|---:|---:|",
]

for name, group in groups.items():
    for p in (1, 2, 4, 8):
        row = group[p]
        e = row["karp_flatt"]
        e_text = "-" if e is None else f"{e:.4f}"
        lines.append(
            f"| {name} | {p} | {row['speedup']:.4f} "
            f"| {row['efficiency_percent']:.2f} | {e_text} |"
        )

lines += [
    "",
    "## Effect of chunking and buffering",
    "",
    "| P | A: fine/coarse runtime ratio | B throughput (items/s) "
    "| C throughput (items/s) | C/B throughput ratio |",
    "|---:|---:|---:|---:|---:|",
]

throughput_ratios = {}
for p in (1, 2, 4, 8):
    granularity_ratio = (
        fine[p]["median_seconds"] / coarse[p]["median_seconds"]
    )
    b_rate = queue[p]["total_items"] / queue[p]["median_seconds"]
    c_rate = buffered[p]["total_items"] / buffered[p]["median_seconds"]
    throughput_ratios[p] = c_rate / b_rate
    lines.append(
        f"| {p} | {granularity_ratio:.3f} "
        f"| {b_rate:.2f} | {c_rate:.2f} "
        f"| {throughput_ratios[p]:.2f} |"
    )

lines += [
    "",
    "## Findings and handout criteria",
    "",
    f"- A: At P=8, coarse chunks are "
    f"{fine[8]['median_seconds'] / coarse[8]['median_seconds']:.2f}x "
    "faster than micro-tasks. This supports the importance of amortizing "
    "dispatch and IPC overhead. Timings alone do not isolate master-process "
    "starvation from other overheads.",
    f"- B: Negative scaling T8 > T1: {b_negative}. "
    f"Strictly increasing e(2) < e(4) < e(8): {b_monotonic}. "
    "Queue runtime grows with worker count, but the expected monotonic "
    "Karp-Flatt surge was not reproduced.",
    f"- C: S8 = {c_speedup:.4f}; S8 > 5: {c_speedup > 5}. "
    f"e(8) = {c_e8:.4f}; e(8) <= 0.05: {c_e8 <= 0.05}.",
    f"- C/B throughput at P=8 = {throughput_ratios[8]:.2f}x; "
    f"greater than 10x: {throughput_ratios[8] > 10}.",
    "",
    "Buffering greatly reduces queue messages and improves throughput, "
    "but the requested near-linear eight-process scaling was not achieved. "
    "The measured C runtime is lowest at four processes. Startup costs, "
    "scheduling and heterogeneous CPU cores may contribute; these causes "
    "were not independently isolated.",
    "",
    "B and C use different input sizes, so C/B is a throughput comparison "
    "at the handout's workloads, not an equal-work runtime speedup.",
    "",
    "Karp-Flatt describes scaling overhead but cannot uniquely establish "
    "a physical cause such as cache-line contention or bus saturation. "
    "All actual measurements are retained, including unmet targets.",
    "",
    "## Formulas",
    "",
    "- S(p) = T1 / Tp",
    "- E(p) = S(p) / p * 100%",
    "- e(p) = (p * Tp / T1 - 1) / (p - 1), for p > 1",
    "- Throughput = total items / elapsed time",
]

output = ROOT / "RESULTS_B.md"
output.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(output.read_text(encoding="utf-8"))
