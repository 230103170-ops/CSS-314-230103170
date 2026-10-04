#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <omp.h>

#define N 13170000ULL
#define REPEATS 100

typedef struct {
    volatile unsigned long long value;
} Counter;

typedef struct {
    volatile unsigned long long value;
    char padding[128 - sizeof(unsigned long long)];
} PaddedCounter;

int main(void) {
    int threads = omp_get_max_threads();

    Counter *shared = calloc(threads, sizeof(Counter));
    PaddedCounter *padded = calloc(threads, sizeof(PaddedCounter));

    double start, end;

    /* Experiment 1: counters next to each other */
    start = omp_get_wtime();

    #pragma omp parallel
    {
        int tid = omp_get_thread_num();

        for (int r = 0; r < REPEATS; r++) {
            for (unsigned long long i = tid; i < N; i += threads) {
                shared[tid].value++;
            }
        }
    }

    end = omp_get_wtime();
    double false_time = end - start;

    /* Experiment 2: padded counters */
    start = omp_get_wtime();

    #pragma omp parallel
    {
        int tid = omp_get_thread_num();

        for (int r = 0; r < REPEATS; r++) {
            for (unsigned long long i = tid; i < N; i += threads) {
                padded[tid].value++;
            }
        }
    }

    end = omp_get_wtime();
    double padded_time = end - start;

    unsigned long long sum1 = 0;
    unsigned long long sum2 = 0;

    for (int i = 0; i < threads; i++) {
        sum1 += shared[i].value;
        sum2 += padded[i].value;
    }

    printf("Threads: %d\n", threads);
    printf("False sharing time: %.6f seconds\n", false_time);
    printf("Padded time: %.6f seconds\n", padded_time);
    printf("False/Padded ratio: %.3fx\n", false_time / padded_time);
    printf("Checksum false: %llu\n", sum1);
    printf("Checksum padded: %llu\n", sum2);

    free(shared);
    free(padded);

    return 0;
}
