# Task 07: Maximum Tolerable Serial Fraction

Given:
- P = 8192 processors
- Required scaled speedup: S(P) >= 7500

Gustafson's formula:

S(P) = P - alpha(P-1)

We need:

P - alpha(P-1) >= 7500

Rearrange:

alpha(P-1) <= P - 7500

alpha <= (P - 7500)/(P-1)

Substitute P = 8192:

alpha <= (8192 - 7500)/(8192 - 1)

alpha <= 692/8191

alpha <= 0.084483

As a percentage:

alpha <= 8.4483%

## Answer

The maximum tolerable serial fraction is approximately 8.45%.

If the serial fraction is greater than this value, the required speedup of 7500 cannot be achieved under Gustafson's model.
