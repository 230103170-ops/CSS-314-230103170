# Task 09: Multi-Component Serial Overhead

Given:
- I/O overhead = 2%
- Boundary synchronization = 6%
- Parallel computation = 92%
- Total serial fraction alpha = 0.02 + 0.06 = 0.08
- Processor counts: 512 and 2048

## 1. Serial Fraction

alpha = 0.02 + 0.06 = 0.08

Parallel fraction:

p = 1 - 0.08 = 0.92

## 2. Gustafson Speedup

S(P) = P - alpha(P-1)

### For 512 processors

S(512) = 512 - 0.08(511)

S(512) = 512 - 40.88

S(512) = 471.12

Efficiency:

E(512) = 471.12/512 = 92.0156%

### For 2048 processors

S(2048) = 2048 - 0.08(2047)

S(2048) = 2048 - 163.76

S(2048) = 1884.24

Efficiency:

E(2048) = 1884.24/2048 = 92.00195%

## Results

| Component | Fraction |
|---|---:|
| I/O | 2% |
| Boundary synchronization | 6% |
| Parallel computation | 92% |
| Total serial fraction | 8% |

| P | Speedup | Efficiency |
|---:|---:|---:|
| 512 | 471.12 | 92.0156% |
| 2048 | 1884.24 | 92.0020% |

## Interpretation

I/O and boundary synchronization together account for 8% of the normalized runtime.

Even though the parallel computation dominates, serial overhead limits the asymptotic efficiency to 92%.

Reducing I/O and synchronization overhead can improve scalability.
