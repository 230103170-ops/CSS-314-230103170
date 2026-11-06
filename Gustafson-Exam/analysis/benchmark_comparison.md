# Weak Scaling: Benchmark Comparison

Hardware: Apple M4, 10 CPU cores, 16 GB RAM

## 500,000 iterations

| Processes | Average time (s) | Efficiency (%) |
|---:|---:|---:|
| 1 | 0.0542 | 100.00 |
| 2 | 0.0470 | 115.41 |
| 4 | 0.0544 | 99.75 |
| 8 | 0.0836 | 64.89 |
| 10 | 0.1000 | 54.21 |

## 5,000,000 iterations

| Processes | Average time (s) | Efficiency (%) |
|---:|---:|---:|
| 1 | 0.2237 | 100.00 |
| 2 | 0.2291 | 97.66 |
| 4 | 0.2465 | 90.73 |
| 8 | 0.3618 | 61.83 |
| 10 | 0.4107 | 54.46 |

## Conclusion

The larger workload provides a more meaningful comparison. However, execution time increases at higher process counts. Multiprocessing overhead and workload characteristics affect weak scaling performance.
