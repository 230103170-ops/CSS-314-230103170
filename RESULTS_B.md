# Scalability Diagnostics — Variant B

Symbat Aldanova — 230103170

## Hardware and method

- CPU: Apple M4
- Physical cores: 10
- Logical cores: 10
- Cache-line size: 128 bytes
- OS: macOS-26.5.2-arm64-arm-64bit
- Python: 3.12.7
- Process start method: spawn
- Three measurements per configuration; reported times are medians.
- Timings include process startup, communication and shutdown.
- A: 1,000,000 Collatz inputs; chunksize 1 versus 10,000.
- B: 400,000 records sent individually through a shared queue.
- C: 10,000,000 records, locally aggregated in batches of 10,000.
- B and C restart the i % 7 sequence in each worker, following the handout.
- Checksums are validated against each configuration's expected result.
- Total work is fixed across process counts within each experiment.

## Measurements

| Configuration | T1 (s) | T2 (s) | T4 (s) | T8 (s) | S8 | e(2) | e(8) |
|---|---:|---:|---:|---:|---:|---:|---:|
| A: Micro (k=1) | 12.082258 | 10.224260 | 12.877681 | 13.494881 | 0.8953 | 0.6924 | 1.1336 |
| A: Coarse (k=10000) | 4.532073 | 2.315462 | 1.246526 | 0.943984 | 4.8010 | 0.0218 | 0.0952 |
| B: Queue | 2.059743 | 2.542022 | 2.632384 | 2.893234 | 0.7119 | 1.4683 | 1.4625 |
| C: Buffered | 0.387350 | 0.219493 | 0.140031 | 0.141120 | 2.7448 | 0.1333 | 0.2735 |

## Detailed scaling

| Configuration | P | Speedup | Efficiency (%) | e(p) |
|---|---:|---:|---:|---:|
| A: Micro (k=1) | 1 | 1.0000 | 100.00 | - |
| A: Micro (k=1) | 2 | 1.1817 | 59.09 | 0.6924 |
| A: Micro (k=1) | 4 | 0.9382 | 23.46 | 1.0878 |
| A: Micro (k=1) | 8 | 0.8953 | 11.19 | 1.1336 |
| A: Coarse (k=10000) | 1 | 1.0000 | 100.00 | - |
| A: Coarse (k=10000) | 2 | 1.9573 | 97.87 | 0.0218 |
| A: Coarse (k=10000) | 4 | 3.6358 | 90.89 | 0.0334 |
| A: Coarse (k=10000) | 8 | 4.8010 | 60.01 | 0.0952 |
| B: Queue | 1 | 1.0000 | 100.00 | - |
| B: Queue | 2 | 0.8103 | 40.51 | 1.4683 |
| B: Queue | 4 | 0.7825 | 19.56 | 1.3707 |
| B: Queue | 8 | 0.7119 | 8.90 | 1.4625 |
| C: Buffered | 1 | 1.0000 | 100.00 | - |
| C: Buffered | 2 | 1.7647 | 88.24 | 0.1333 |
| C: Buffered | 4 | 2.7662 | 69.15 | 0.1487 |
| C: Buffered | 8 | 2.7448 | 34.31 | 0.2735 |

## Effect of chunking and buffering

| P | A: fine/coarse runtime ratio | B throughput (items/s) | C throughput (items/s) | C/B throughput ratio |
|---:|---:|---:|---:|---:|
| 1 | 2.666 | 194199.03 | 25816442.28 | 132.94 |
| 2 | 4.416 | 157355.05 | 45559565.43 | 289.53 |
| 4 | 10.331 | 151953.52 | 71412843.77 | 469.97 |
| 8 | 14.296 | 138253.60 | 70861531.38 | 512.55 |

## Findings and handout criteria

- A: At P=8, coarse chunks are 14.30x faster than micro-tasks. This supports the importance of amortizing dispatch and IPC overhead. Timings alone do not isolate master-process starvation from other overheads.
- B: Negative scaling T8 > T1: True. Strictly increasing e(2) < e(4) < e(8): False. Queue runtime grows with worker count, but the expected monotonic Karp-Flatt surge was not reproduced.
- C: S8 = 2.7448; S8 > 5: False. e(8) = 0.2735; e(8) <= 0.05: False.
- C/B throughput at P=8 = 512.55x; greater than 10x: True.

Buffering greatly reduces queue messages and improves throughput, but the requested near-linear eight-process scaling was not achieved. The measured C runtime is lowest at four processes. Startup costs, scheduling and heterogeneous CPU cores may contribute; these causes were not independently isolated.

B and C use different input sizes, so C/B is a throughput comparison at the handout's workloads, not an equal-work runtime speedup.

Karp-Flatt describes scaling overhead but cannot uniquely establish a physical cause such as cache-line contention or bus saturation. All actual measurements are retained, including unmet targets.

## Formulas

- S(p) = T1 / Tp
- E(p) = S(p) / p * 100%
- e(p) = (p * Tp / T1 - 1) / (p - 1), for p > 1
- Throughput = total items / elapsed time
