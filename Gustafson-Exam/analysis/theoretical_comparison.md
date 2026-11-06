# Amdahl's Law vs Gustafson's Law

Serial fraction (alpha): 0.05

| Processors | Amdahl Speedup | Gustafson Speedup |
|---:|---:|---:|
| 1 | 1.000 | 1.000 |
| 2 | 1.905 | 1.950 |
| 4 | 3.478 | 3.850 |
| 8 | 5.926 | 7.650 |
| 10 | 6.897 | 9.550 |

## Analysis

Amdahl's Law assumes a fixed problem size. Gustafson's Law assumes that the problem size increases with the number of processors.

For 10 processors, Amdahl's Law predicts a speedup of approximately 6.897, while Gustafson's Law predicts 9.550.

This demonstrates the advantage of scaled parallel workloads.
