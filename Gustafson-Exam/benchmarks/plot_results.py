import csv
import matplotlib.pyplot as plt


def read_results(path):
    with open(path) as file:
        rows = list(csv.DictReader(file))

    processes = [int(row["processes"]) for row in rows]
    times = [float(row["average_time"]) for row in rows]
    baseline = times[0]
    efficiency = [baseline / t * 100 for t in times]

    return processes, times, efficiency


experiments = [
    ("500K iterations",
     "benchmarks/weak_scale_bench/results_500k.csv"),
    ("5M iterations",
     "benchmarks/weak_scale_bench/results_5m.csv")
]

for label, path in experiments:
    processes, times, efficiency = read_results(path)

    plt.figure(figsize=(8, 5))
    plt.plot(processes, times, marker="o")
    plt.title(f"Weak Scaling Execution Time - {label}")
    plt.xlabel("Number of Processes")
    plt.ylabel("Average Execution Time (seconds)")
    plt.grid(True)
    plt.xticks(processes)
    plt.tight_layout()

    filename = label.replace(" ", "_").lower()
    plt.savefig(f"plots/{filename}_time.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(processes, efficiency, marker="o")
    plt.title(f"Weak Scaling Efficiency - {label}")
    plt.xlabel("Number of Processes")
    plt.ylabel("Efficiency (%)")
    plt.grid(True)
    plt.xticks(processes)
    plt.tight_layout()

    plt.savefig(f"plots/{filename}_efficiency.png", dpi=150)
    plt.close()

print("Four graphs created successfully in plots/")
