# Task 15: Energy-Aware Scaling

## 1. Power and Energy

Energy consumption is:

Energy = Power * Time

Let:
- P_active be the power of one active processor.
- P_idle be the power of one idle processor.
- N be the total number of available processors.
- P be the number of active processors.
- T be the common wall-clock runtime.

Assume the same wall-clock runtime T for both configurations.

## 2. One Active Processor

One processor is active and N-1 processors are idle.

Total system power:

Power_1 = P_active + (N-1)P_idle

Energy:

Energy_1 = [P_active + (N-1)P_idle]T

## 3. P Active Processors

P processors are active and N-P processors are idle.

Total system power:

Power_P = P*P_active + (N-P)P_idle

Energy:

Energy_P = [P*P_active + (N-P)P_idle]T

## 4. Energy Difference

Subtract:

Energy_P - Energy_1

= (P-1)(P_active-P_idle)T

If P_active is greater than P_idle, activating more processors increases energy consumption for the same wall-clock duration.

## 5. Important Distinction

In practical parallel computing, more processors often reduce execution time.

For a fixed amount of work, the correct comparison is:

Energy = Power * Execution Time

A configuration with more processors may consume more power but finish earlier.

Therefore, lower execution time does not automatically mean lower energy consumption.

## 6. Energy-Aware Optimization

Possible techniques include:
- Dynamic voltage and frequency scaling.
- Turning off unused processors.
- Selecting an efficient processor count.
- Reducing memory movement.
- Improving cache locality.
- Minimizing communication and synchronization.

## Conclusion

Energy-aware parallel computing must consider both power and execution time. The fastest configuration is not necessarily the most energy-efficient.
