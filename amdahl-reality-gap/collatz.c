#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <omp.h>

#define N 13170000ULL
#define MOD 1000000007ULL

unsigned long collatz_steps(unsigned long long n) {
    unsigned long steps = 0;

    while (n != 1) {
        if (n % 2 == 0) {
            n /= 2;
        } else {
            n = 3 * n + 1;
        }
        steps++;
    }

    return steps;
}

double elapsed_seconds(struct timespec start, struct timespec end) {
    return (end.tv_sec - start.tv_sec) +
           (end.tv_nsec - start.tv_nsec) / 1000000000.0;
}

int main(void) {
    unsigned long max_steps = 0;
    unsigned long long checksum = 0;

    struct timespec start, end;

    clock_gettime(CLOCK_MONOTONIC, &start);

    #pragma omp parallel for reduction(max:max_steps) reduction(+:checksum) schedule(static)
    for (unsigned long long i = 1; i <= N; i++) {
        unsigned long steps = collatz_steps(i);

        if (steps > max_steps) {
            max_steps = steps;
        }

        checksum += steps;
    }

    checksum %= MOD;

    clock_gettime(CLOCK_MONOTONIC, &end);

    double time_taken = elapsed_seconds(start, end);

    printf("N: %llu\n", N);
    printf("Threads: %d\n", omp_get_max_threads());
    printf("Max Collatz stopping steps: %lu\n", max_steps);
    printf("Checksum mod 1000000007: %llu\n", checksum);
    printf("Time: %.6f seconds\n", time_taken);

    return 0;
}
