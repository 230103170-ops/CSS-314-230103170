# Task 06: Parametric Gustafson Speedup Table

Given:
- Serial fraction: alpha = 0.04
- Processor counts: P = 16, 64, 256, 1024, 4096, 16384

Gustafson's formula:

S(P) = P - alpha(P-1)

Efficiency:

E(P) = S(P)/P * 100%

## Calculations

For P = 16:

S(16) = 16 - 0.04(15) = 15.40

E(16) = 15.40/16 * 100 = 96.25%

The same formulas are applied to every processor count.

## Results

| P | Gustafson Speedup | Efficiency |
|---:|---:|---:|
| 16 | 15.40 | 96.2500% |
| 64 | 61.48 | 96.0625% |
| 256 | 245.80 | 96.0156% |
| 1024 | 983.08 | 96.0039% |
| 4096 | 3932.20 | 96.0010% |
| 16384 | 15728.68 | 96.0002% |

## Interpretation

As P increases, the speedup approaches linear scaling.

Efficiency approaches 1 - alpha = 0.96, or 96%.

The serial fraction limits the efficiency, but the scaled speedup continues to grow with processor count.
