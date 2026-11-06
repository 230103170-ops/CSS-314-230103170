# Task 12: Communication Penalty in Gustafson's Law

## 1. Original Gustafson Model

The original scaled speedup is:

S_G(P) = P - alpha(P-1)

This model assumes that communication and synchronization overhead are negligible or included in the measured serial and parallel fractions.

## 2. Add Communication Overhead

Let C(P) represent communication overhead relative to normalized computational runtime.

A simple modified model is:

S_modified(P) = [P - alpha(P-1)] / [1 + C(P)]

This is an illustrative extension, not the original Gustafson equation.

## 3. Logarithmic Communication

For a tree-based collective operation, communication may grow approximately as:

C(P) = k log2(P)

where k is a communication-cost coefficient.

Then:

S_modified(P) =
[P - alpha(P-1)] / [1 + k log2(P)]

The communication penalty grows slowly, but it can reduce efficiency as P increases.

## 4. Surface-to-Volume Communication

For a regular three-dimensional domain decomposition, each subdomain communicates through boundaries.

A simplified communication model is:

C(P) = k P^(1/2)

This can represent a situation where communication cost grows with the number of subdomain boundary elements under a particular fixed-local-domain model.

Then:

S_modified(P) =
[P - alpha(P-1)] / [1 + k P^(1/2)]

## 5. Interpretation

Without communication overhead, Gustafson speedup grows approximately linearly.

With communication overhead:
- Speedup increases more slowly.
- Efficiency decreases.
- At sufficiently large P, communication can dominate computation.

The actual communication function depends on the algorithm, topology, message size, and data distribution.

## Conclusion

A realistic scalability model must account for communication and synchronization costs. The original Gustafson equation is an idealized model.
