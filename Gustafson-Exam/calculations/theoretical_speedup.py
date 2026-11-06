# Gustafson's Law - Theoretical Speedup

def gustafson_speedup(processors, serial_fraction):
    return processors - serial_fraction * (processors - 1)


alpha = 0.05
processor_counts = [1, 2, 4, 8, 10]

print("GUSTAFSON'S LAW")
print("Serial fraction:", alpha)
print("-" * 45)
print(f"{'Processors':<15}{'Speedup':<15}{'Efficiency':<15}")

for n in processor_counts:
    speedup = gustafson_speedup(n, alpha)
    efficiency = speedup / n * 100

    print(f"{n:<15}{speedup:<15.2f}{efficiency:<15.2f}%")
