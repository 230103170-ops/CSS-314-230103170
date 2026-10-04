import matplotlib.pyplot as plt
import numpy as np

# Measured sequential baseline
T_seq = 1.4786675

# Real OpenMP measurements
threads = np.array([1, 2, 4, 8, 10, 16])
times = np.array([
    1.483203,
    0.794056,
    0.450845,
    0.274151,
    0.239414,
    0.238670
])

measured_speedup = T_seq / times

# Estimate parallel fraction p from the measured 2-thread result
S2 = T_seq / times[1]
p = 2 * (1 - 1 / S2)

# Amdahl theoretical speedup
k = np.linspace(1, 16, 200)
amdahl_speedup = 1 / ((1 - p) + p / k)

plt.figure(figsize=(8, 5))

plt.plot(
    threads,
    measured_speedup,
    marker="o",
    label="Measured speedup"
)

plt.plot(
    k,
    amdahl_speedup,
    linestyle="--",
    label=f"Amdahl prediction (p={p:.3f})"
)

plt.xlabel("Number of threads")
plt.ylabel("Speedup")
plt.title("OpenMP Collatz Scaling — Apple M4")
plt.xticks([1, 2, 4, 8, 10, 16])
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig("speedup_plot.png", dpi=300)

print(f"S2 = {S2:.4f}")
print(f"Estimated parallel fraction p = {p:.4f} ({p*100:.2f}%)")
print("Created speedup_plot.png")
