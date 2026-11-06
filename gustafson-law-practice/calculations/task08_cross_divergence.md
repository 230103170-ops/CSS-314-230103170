# Task 08: Amdahl vs Gustafson Cross-Divergence

Given:
- Serial fraction = 0.08
- Parallel fraction = 0.92
- Processor count P = 128

## 1. Amdahl's Law

S_A(P) = 1 / [alpha + (1-alpha)/P]

S_A(128) = 1 / [0.08 + 0.92/128]

S_A(128) = 1 / 0.0871875

S_A(128) = 11.4695

## 2. Gustafson's Law

S_G(P) = P - alpha(P-1)

S_G(128) = 128 - 0.08(127)

S_G(128) = 128 - 10.16

S_G(128) = 117.84

## 3. Difference

Absolute difference:

117.84 - 11.4695 = 106.3705

Relative increase compared with Amdahl:

[(117.84 - 11.4695)/11.4695] * 100

= 927.42%

Gustafson's result is approximately 10.27 times the Amdahl result.

## Answer and Interpretation

| Model | Speedup |
|---|---:|
| Amdahl | 11.4695 |
| Gustafson | 117.84 |
| Absolute difference | 106.3705 |

The large difference occurs because Amdahl assumes a fixed total workload, while Gustafson assumes that the workload grows with processor count.

The percentage comparison above is measured relative to Amdahl's speedup.
