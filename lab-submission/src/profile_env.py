import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path

from salt import get_student_params


def sysctl(key):
    result = subprocess.run(
        ["sysctl", "-n", key],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--student-id", required=True)
    args = parser.parse_args()

    results = Path(__file__).resolve().parent.parent / "results"
    results.mkdir(parents=True, exist_ok=True)

    physical = sysctl("hw.physicalcpu")
    logical = sysctl("hw.logicalcpu")

    profile = {
        "cpu_model": sysctl("machdep.cpu.brand_string"),
        "architecture": platform.machine(),
        "microarchitecture": None,
        "microarchitecture_note": (
            "Not directly reported by the queried macOS sysctl keys."
        ),
        "base_frequency_hz": sysctl("hw.cpufrequency"),
        "physical_cores": physical,
        "logical_threads": logical,
        "smt_detected": logical > physical if physical and logical else None,
        "cache_line_bytes": sysctl("hw.cachelinesize"),
        "l1_data_cache_bytes": sysctl("hw.l1dcachesize"),
        "l2_cache_bytes": sysctl("hw.l2cachesize"),
        "l3_cache_bytes": sysctl("hw.l3cachesize"),
        "memory_bytes": sysctl("hw.memsize"),
        "os": platform.system(),
        "macos_version": platform.mac_ver()[0],
        "kernel_version": platform.release(),
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "performance_levels": {},
        "notes": [
            "Null means the information was not exposed by sysctl.",
            "Cache sizes may differ between performance and efficiency cores.",
            "Per-level cache sizes are recorded as reported, not summed.",
        ],
    }

    levels = sysctl("hw.nperflevels")
    for level in range(levels if isinstance(levels, int) else 0):
        prefix = f"hw.perflevel{level}"
        profile["performance_levels"][str(level)] = {
            field: sysctl(f"{prefix}.{field}")
            for field in (
                "name", "physicalcpu", "logicalcpu",
                "l1dcachesize", "l1icachesize",
                "l2cachesize", "cpusperl2",
            )
        }

    outputs = {
        "host_profile.json": profile,
        "salted_params.json": get_student_params(args.student_id),
    }
    for filename, data in outputs.items():
        path = results / filename
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"Created: {path}")
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
