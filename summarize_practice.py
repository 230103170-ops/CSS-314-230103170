import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "practice_results"


def read(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


hardware = read("hardware.json")
reports = {name: read(f"{name}.json") for name in ("A", "B", "C")}
rows = {
    name: {row["p"]: row for row in report["rows"]}
    for name, report in reports.items()
}

a = rows["A"]
b = rows["B"]
c = rows["C"]

e2 = a[2]["karp_flatt"]
e4 = a[4]["karp_flatt"]
ratio = e4 / e2 if e2 != 0 else None
a_flat = ratio is not None and 0.80 <= ratio <= 1.25

b_slower = b[4]["median_seconds"] > b[1]["median_seconds"]
b_rising = b[4]["karp_flatt"] > b[2]["karp_flatt"]

c_faster = c[4]["median_seconds"] < c[1]["median_seconds"]
c_efficient = c[4]["efficiency_percent"] > 70

diagnoses = {
    "A": (
        "Serial sleep included; flat-e criterion met."
        if a_flat else
        "Serial sleep included; measured e does not meet the flat-e criterion."
    ),
    "B": (
        "Shared-lock run slows down at P=4 and e increases."
        if b_slower and b_rising else
        "Shared-lock contention introduced; expected diagnostic pattern is incomplete."
    ),
    "C": (
        "Privatization improves runtime; E4 exceeds 70%."
        if c_faster and c_efficient else
        "Privatization implemented; the full scaling criterion is not met."
    ),
}

lines = [
    "# Karp-Flatt Practice Lab",
    "",
    "Symbat Aldanova — 230103170",
    "",
    "## Hardware and method",
    "",
    f"- CPU: {hardware['cpu_model']}",
    f"- Physical cores: {hardware['physical_cores']}",
    f"- Logical cores: {hardware['logical_cores']}",
    f"- Cache line: {hardware['cache_line_bytes']} bytes",
    f"- OS: {hardware['os']}",
    f"- Python: {hardware['python']}",
    f"- Process start method: {reports['A']['start_method']}",
    "- Three runs per worker count; tables use median wall-clock time.",
    "- Timing includes process startup, coordination and shutdown.",
    "- A: 16 chunks of size 2,000,000 plus a 0.40-second serial pause.",
    "- B: 2,000,000 total increments with a shared lock.",
    "- C: 20,000,000 total increments using local counters.",
    "- Work is fixed across worker counts within each experiment.",
    "",
    "## Measured results",
    "",
    "| Experiment | T1 (s) | T2 (s) | T4 (s) | e(2) | e(4) | Diagnosis |",
    "|---|---:|---:|---:|---:|---:|---|",
]

for name in ("A", "B", "C"):
    r = rows[name]
    lines.append(
        f"| {name} "
        f"| {r[1]['median_seconds']:.6f} "
        f"| {r[2]['median_seconds']:.6f} "
        f"| {r[4]['median_seconds']:.6f} "
        f"| {r[2]['karp_flatt']:.6f} "
        f"| {r[4]['karp_flatt']:.6f} "
        f"| {diagnoses[name]} |"
    )

lines += [
    "",
    "## Speedup and efficiency",
    "",
    "| Experiment | Processes | Speedup | Efficiency (%) |",
    "|---|---:|---:|---:|",
]

for name in ("A", "B", "C"):
    for p in (1, 2, 4):
        r = rows[name][p]
        lines.append(
            f"| {name} | {p} | {r['speedup']:.4f} "
            f"| {r['efficiency_percent']:.2f} |"
        )

ratio_text = "undefined" if ratio is None else f"{ratio:.4f}"
lines += [
    "",
    "## Handout criteria",
    "",
    f"- A: e(4)/e(2) = {ratio_text}; within [0.80, 1.25]: {a_flat}.",
    f"- B: T4 > T1: {b_slower}; e(4) > e(2): {b_rising}.",
    "  The magnitude of the e increase is shown above; "
    "the handout does not specify a numerical threshold for 'much greater'.",
    f"- C: T4 < T1: {c_faster}; E4 = {c[4]['efficiency_percent']:.2f}%; "
    f"E4 > 70%: {c_efficient}.",
    "",
    "## Interpretation and limitations",
    "",
    "The deliberate serial pause in A, shared locking in B, and local "
    "accumulation in C are known implementation differences. Karp-Flatt "
    "summarizes measured scaling overhead, but does not uniquely identify "
    "its physical cause. Process startup, scheduling, heterogeneous cores "
    "and measurement variability also affect the values. Expected numbers "
    "in the handout are not guaranteed on this machine. B and C use "
    "different total workloads, so their raw runtimes are not a direct "
    "equal-work speedup comparison. No timings were adjusted to match targets.",
    "",
    "Formula: S(p) = T1/Tp; e(p) = (p*Tp/T1 - 1)/(p - 1), for p > 1.",
]

output = ROOT / "RESULTS.md"
output.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(output.read_text(encoding="utf-8"))
