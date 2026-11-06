# Weak Scaling Analysis

Hardware: Apple M4, 10 CPU cores

| Processes | Average Time (s) | Efficiency (%) |
|---:|---:|---:|
| 1 | 0.0542 | 100.00 |
| 2 | 0.0470 | 115.41 |
| 4 | 0.0544 | 99.75 |
| 8 | 0.0836 | 64.89 |
| 10 | 0.1000 | 54.21 |

## Conclusion

The experiment shows that execution time increases when the number of processes becomes large. Process creation and multiprocessing overhead affect the performance of this relatively small workload.
