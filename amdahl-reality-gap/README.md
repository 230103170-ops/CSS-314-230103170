# Amdahl Reality Gap Practicum

Student ID: 230103170

## Hardware

- Apple M4
- 10 CPU cores (4 Performance + 6 Efficiency)
- 16 GB RAM
- macOS ARM64

## Workload

Collatz workload:

N = 13,170,000

## OpenMP Setup

Install OpenMP runtime on macOS:

brew install libomp

## Compile

Collatz benchmark:

clang -O2 -Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include collatz.c -L/opt/homebrew/opt/libomp/lib -lomp -o collatz

False sharing benchmark:

clang -O2 -Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include false_sharing.c -L/opt/homebrew/opt/libomp/lib -lomp -o false_sharing

Scheduling benchmark:

clang -O2 -Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include scheduling.c -L/opt/homebrew/opt/libomp/lib -lomp -o scheduling

## Run

Example OpenMP scaling runs:

OMP_NUM_THREADS=1 ./collatz
OMP_NUM_THREADS=2 ./collatz
OMP_NUM_THREADS=4 ./collatz
OMP_NUM_THREADS=8 ./collatz
OMP_NUM_THREADS=10 ./collatz
OMP_NUM_THREADS=16 ./collatz

Run false-sharing experiment:

./false_sharing

Run scheduling experiment:

./scheduling

## Results

Raw benchmark results are stored in `results.csv`.

The OpenMP speedup graph is stored in `speedup_plot.png`.

The final analysis and answers are provided in `analysis.pdf`.
