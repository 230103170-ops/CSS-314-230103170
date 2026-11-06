# Gustafson's Law

## 1. Introduction

Gustafson's Law describes how parallel computing performance improves when the problem size increases with the number of processors.

Unlike Amdahl's Law, which assumes a fixed problem size, Gustafson's Law assumes that larger systems can solve larger problems in approximately the same amount of time.

## 2. Mathematical Formula

The formula is:

S(N) = N - alpha * (N - 1)

Where:
- S(N) is the scaled speedup.
- N is the number of processors.
- alpha is the serial fraction of the program.
- (1 - alpha) is the parallel fraction.

## 3. Example

Assume:
- N = 10 processors
- alpha = 0.05

S(10) = 10 - 0.05 * (10 - 1)

S(10) = 10 - 0.45

S(10) = 9.55

The theoretical speedup is 9.55.

## 4. Interpretation

Gustafson's Law shows that parallel computing becomes more useful when the workload grows with the number of processors.

A larger number of processors can process a larger problem without requiring a proportional increase in execution time.

## 5. Limitations

- Communication overhead can reduce performance.
- Synchronization between processors takes time.
- Memory bandwidth can become a bottleneck.
- Not every part of a program can run in parallel.

## 6. Conclusion

Gustafson's Law demonstrates the potential of parallel computing for large-scale problems. It explains why increasing the number of processors can provide significant benefits when the problem size scales with the available computing resources.
