# Task 11: Sun-Ni Memory-Bounded Speedup vs Gustafson

## 1. Introduction

Sun and Ni introduced the memory-bounded speedup model to explain how parallel performance depends on both processor count and available memory.

The model considers three approaches:
- Fixed-size speedup: Amdahl's Law.
- Fixed-time speedup: Gustafson's Law.
- Memory-bounded speedup: workload grows according to available memory.

## 2. General Simplified Model

A commonly used simplified expression is:

S(P) = [(1-alpha)g(P) + alpha] / [(1-alpha)g(P)/P + alpha]

where:
- P is the number of processors.
- alpha is the serial fraction.
- g(P) describes how the workload grows with system capacity.

Special cases:

If g(P) = 1:

S(P) = 1 / [alpha + (1-alpha)/P]

This is Amdahl's Law.

If g(P) = P:

S(P) = alpha + P(1-alpha)

This is Gustafson's scaled speedup.

## 3. Memory-Bounded Example: Matrix Multiplication

For multiplying two N x N matrices:

- Memory requirement is proportional to N^2.
- Computation is proportional to N^3.

If total memory grows proportionally to P:

N^2 is proportional to P.

Therefore:

N is proportional to P^(1/2).

The computational workload grows as:

N^3 is proportional to P^(3/2).

Thus, the workload growth function is:

g(P) = P^(3/2)

Substituting:

S(P) = [alpha + (1-alpha)P^(3/2)] /
       [alpha + (1-alpha)P^(1/2)]

This is a simplified memory-bounded model for this example.

## 4. When Gustafson Overestimates Throughput

Gustafson's Law may overestimate throughput when:
- Memory bandwidth is saturated.
- Communication increases rapidly.
- Data replication consumes memory.
- Synchronization becomes expensive.
- The workload cannot grow proportionally to processor count.

## 5. When Gustafson May Underestimate Throughput

Measured performance may exceed a simple Gustafson prediction when:
- Larger workloads improve cache utilization.
- Vectorization becomes more effective.
- Communication is overlapped with computation.
- The smaller baseline workload has disproportionate fixed overhead.

Such results must be measured carefully. They are not guaranteed.

## Conclusion

Gustafson models fixed-time scaling. Sun-Ni extends the analysis by connecting workload growth to memory capacity.

Reference:
X.-H. Sun and L. M. Ni, "Scalable Problems and Memory-Bounded Speedup", Journal of Parallel and Distributed Computing, 19(1), 27-37, 1993.
DOI: https://doi.org/10.1006/jpdc.1993.1087
