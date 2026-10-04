#include <stdio.h>
#include <stdint.h>
#include <omp.h>

#define N 13170000ULL
#define MOD 1000000007ULL

unsigned long collatz_steps(unsigned long long n) {
    unsigned long steps = 0;

    while (n != 1) {
        if (n % 2 == 0)
            n /= 2;
        else
            n = 3 * n + 1;

        steps++;
    }

    return steps;
}

void run_test(const char *name, omp_sched_t schedule, int chunk) {
    unsigned long max_steps = 0;
    unsigned long long checksum = 0;

    omp_set_schedule(schedule, chunk);

    double start = omp_get_wtime();

    #pragma omp parallel for schedule(runtime) \
        reduction(max:max_steps) reduction(+:checksum)
    for (unsigned long long i = 1; i <= N; i++) {
        unsigned long steps = collatz_steps(i);

        if (steps > max_steps)
            max_steps = steps;

        checksum += steps;
    }

    double end = omp_get_wtime();

    checksum %= MOD;

    printf("%-15s %.6f s  max=%lu  checksum=%llu\n",
           name,
           end - start,
           max_steps,
           checksum);
}

int main(void) {
    printf("Threads: %d\n", omp_get_max_threads());

    run_test("static",        omp_sched_static, 0);
    run_test("static,1000",   omp_sched_static, 1000);
    run_test("dynamic,100",   omp_sched_dynamic, 100);
    run_test("dynamic,10000", omp_sched_dynamic, 10000);
    run_test("guided",        omp_sched_guided, 0);

    return 0;
}
