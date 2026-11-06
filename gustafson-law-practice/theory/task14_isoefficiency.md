# Task 14: Isoefficiency and Gustafson-Compliant Weak Scaling

## 1. Definition

Isoefficiency describes how quickly the total problem size must grow with processor count to maintain a constant parallel efficiency.

Parallel efficiency is:

E = T1 / (P * TP)

where:
- T1 is serial execution time.
- TP is parallel execution time.
- P is processor count.

Using the overhead formulation:

TP = T1/P + To/P

where To is total parallel overhead.

Therefore:

E = 1 / (1 + To/T1)

## 2. Constant Efficiency Condition

To maintain a fixed efficiency E:

To/T1 = 1/E - 1

For a chosen constant efficiency, overhead must remain proportional to the serial workload.

Therefore:

T1 = Theta(To)

The isoefficiency function describes the minimum problem size required to satisfy this condition.

## 3. Example: Communication Overhead

Suppose total overhead grows as:

To(P) = Theta(P log P)

Then the problem size must grow at least as:

W(P) = Theta(P log P)

to maintain constant efficiency, assuming the serial work is proportional to W.

This is an example, not a universal isoefficiency function.

## 4. Relationship to Gustafson's Law

Gustafson assumes the workload grows as more processors become available.

Isoefficiency provides a more detailed condition:

- It identifies how fast the problem must grow.
- It accounts for overhead growth.
- It shows whether constant efficiency is realistically achievable.

If the problem grows more slowly than the isoefficiency function, efficiency eventually decreases.

## 5. Conclusion

Gustafson describes scaled speedup under fixed-time assumptions.

Isoefficiency explains the problem-size growth needed to preserve a desired efficiency in the presence of parallel overhead.
