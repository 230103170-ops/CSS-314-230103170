# Task 10: Memory-Bounded Weak Scaling

Given:
- Number of nodes: P = 64 or 512
- Memory limit per node: 32 GB
- Total memory grows proportionally to P
- Problem is a cubic three-dimensional grid
- One grid cell requires b bytes

## 1. Total Available Memory

If every node can use its full memory capacity:

M_total(P) = 32 * P GB

For 64 nodes:

M_total(64) = 32 * 64 = 2048 GB

For 512 nodes:

M_total(512) = 32 * 512 = 16384 GB

## 2. Cubic Grid Memory

For a cubic grid with dimension N:

Number of cells = N^3

Memory requirement:

M_grid = b * N^3

The memory constraint is:

b * N^3 <= 32 * P GB

Therefore:

N^3 <= (32 * P * GB_in_bytes)/b

Maximum grid dimension:

N_max = floor[(32 * P * GB_in_bytes / b)^(1/3)]

## 3. Results in Formula Form

Using 32 GiB per node:

For 64 nodes:

N_max = floor[(64 * 32 * 2^30 / b)^(1/3)]

For 512 nodes:

N_max = floor[(512 * 32 * 2^30 / b)^(1/3)]

The dimension grows proportionally to P^(1/3), assuming the bytes per cell remain constant.

## 4. Illustrative Example

If one cell uses 8 bytes:

For 64 nodes:

N_max = floor[(64 * 32 * 2^30 / 8)^(1/3)]

For 512 nodes:

N_max = floor[(512 * 32 * 2^30 / 8)^(1/3)]

These are illustrative estimates, not definitive answers for the assignment.

## 5. Important Missing Information

The task does not specify:
- Bytes required per grid cell.
- Number of variables stored per cell.
- Whether additional memory is needed for ghost cells, temporary arrays, or metadata.
- Whether GB means decimal GB or binary GiB.

Therefore, a unique numerical value for N cannot be calculated without additional assumptions.

## Conclusion

The correct general result is:

N_max = floor[(P * 32 GiB / b)^(1/3)]

where b is the memory required per grid cell.

The global grid dimension scales as P^(1/3), while memory per node remains fixed at 32 GB.
