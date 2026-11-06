# Comparison of Amdahl's Law and Gustafson's Law

def amdahl_speedup(n, alpha):
    return 1 / (alpha + (1 - alpha) / n)


def gustafson_speedup(n, alpha):
    return n - alpha * (n - 1)


alpha = 0.05
processors = [1, 2, 4, 8, 10]

print("AMDAHL'S LAW VS GUSTAFSON'S LAW")
print("Serial fraction:", alpha)
print("-" * 65)
print(f"{'Processors':<15}{'Amdahl':<20}{'Gustafson':<20}")

for n in processors:
    amdahl = amdahl_speedup(n, alpha)
    gustafson = gustafson_speedup(n, alpha)

    print(f"{n:<15}{amdahl:<20.3f}{gustafson:<20.3f}")
