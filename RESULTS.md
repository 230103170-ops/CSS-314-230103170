# Karp-Flatt Practice Lab

Symbat Aldanova — 230103170

## Hardware and method

- CPU: Apple M4
- Physical cores: 10
- Logical cores: 10
- Cache line: 128 bytes
- OS: macOS-26.5.2-arm64-arm-64bit
- Python: 3.12.7
- Process start method: spawn
- Three runs per worker count; tables use median wall-clock time.
- Timing includes process startup, coordination and shutdown.
- A: 16 chunks of size 2,000,000 plus a 0.40-second serial pause.
- B: 2,000,000 total increments with a shared lock.
- C: 20,000,000 total increments using local counters.
- Work is fixed across worker counts within each experiment.

## Measured results

| Experiment | T1 (s) | T2 (s) | T4 (s) | e(2) | e(4) | Diagnosis |
|---|---:|---:|---:|---:|---:|---|
| A | 2.645247 | 1.630385 | 1.045288 | 0.232690 | 0.193543 | Serial sleep included; flat-e criterion met. |
| B | 2.980034 | 9.274576 | 9.030208 | 5.224477 | 3.706983 | Shared-lock contention introduced; expected diagnostic pattern is incomplete. |
| C | 0.339868 | 0.189090 | 0.116442 | 0.112727 | 0.123478 | Privatization improves runtime; E4 exceeds 70%. |

## Speedup and efficiency

| Experiment | Processes | Speedup | Efficiency (%) |
|---|---:|---:|---:|
| A | 1 | 1.0000 | 100.00 |
| A | 2 | 1.6225 | 81.12 |
| A | 4 | 2.5306 | 63.27 |
| B | 1 | 1.0000 | 100.00 |
| B | 2 | 0.3213 | 16.07 |
| B | 4 | 0.3300 | 8.25 |
| C | 1 | 1.0000 | 100.00 |
| C | 2 | 1.7974 | 89.87 |
| C | 4 | 2.9188 | 72.97 |

## Handout criteria

- A: e(4)/e(2) = 0.8318; within [0.80, 1.25]: True.
- B: T4 > T1: True; e(4) > e(2): False.
  The magnitude of the e increase is shown above; the handout does not specify a numerical threshold for 'much greater'.
- C: T4 < T1: True; E4 = 72.97%; E4 > 70%: True.

## Interpretation and limitations

The deliberate serial pause in A, shared locking in B, and local accumulation in C are known implementation differences. Karp-Flatt summarizes measured scaling overhead, but does not uniquely identify its physical cause. Process startup, scheduling, heterogeneous cores and measurement variability also affect the values. Expected numbers in the handout are not guaranteed on this machine. B and C use different total workloads, so their raw runtimes are not a direct equal-work speedup comparison. No timings were adjusted to match targets.

Formula: S(p) = T1/Tp; e(p) = (p*Tp/T1 - 1)/(p - 1), for p > 1.
