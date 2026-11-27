import os
os.environ["NUMBA_THREADING_LAYER"] = "omp"

import time
import hashlib
import json
import numpy as np
import numba as nb

from numba import (
    njit, prange, set_num_threads,
    get_num_threads, get_thread_id
)

STUDENT_NAME = "Symbat Aldanova"
STUDENT_ID = 230103170

assert isinstance(STUDENT_ID, int) and STUDENT_ID > 0
assert (os.cpu_count() or 1) >= 4

# OpenMP initialization
@njit(parallel=True)
def omp_probe():
    workers = np.zeros(64, dtype=np.int64)
    for i in prange(64):
        workers[i] = get_thread_id()
    return workers

worker_ids = omp_probe()
assert nb.threading_layer() == "omp"

# Student-specific parameters
rng = np.random.default_rng(STUDENT_ID)

N_T1 = 4_000_000 + (STUDENT_ID % 991) * 1024
BINS_T1 = 48 + (STUDENT_ID % 17)

data_t1 = rng.integers(
    0, BINS_T1, size=N_T1, dtype=np.int32
)
weights_t1 = rng.uniform(
    0.25, 2.50, size=N_T1
).astype(np.float64)


# TASK 1A: Intentionally unsafe histogram
@njit(parallel=True)
def buggy_hist_omp(indices, weights, num_bins):
    hist = np.zeros(num_bins, dtype=np.int64)
    w_sums = np.zeros(num_bins, dtype=np.float64)

    for i in prange(indices.shape[0]):
        b = indices[i]
        hist[b] += 1
        w_sums[b] += weights[i]

    return hist, w_sums


# TASK 1B: Thread-private histogram
@njit(parallel=True)
def safe_hist_omp(indices, weights, num_bins):
    max_threads = get_num_threads()

    private_hist = np.zeros(
        (max_threads, num_bins), dtype=np.int64
    )
    private_sums = np.zeros(
        (max_threads, num_bins), dtype=np.float64
    )
    worker_hits = np.zeros(max_threads, dtype=np.int64)

    for i in prange(indices.shape[0]):
        tid = get_thread_id()
        b = indices[i]

        private_hist[tid, b] += 1
        private_sums[tid, b] += weights[i]
        worker_hits[tid] += 1

    hist = np.zeros(num_bins, dtype=np.int64)
    w_sums = np.zeros(num_bins, dtype=np.float64)

    # Deterministic row-wise reduction
    for tid in range(max_threads):
        for b in range(num_bins):
            hist[b] += private_hist[tid, b]
            w_sums[b] += private_sums[tid, b]

    return hist, w_sums, worker_hits


# TASK 1C: Race-condition experiment
print("\n========== TASK 1: RACE CONDITION ==========")
print("Student:", STUDENT_NAME)
print("Student ID:", STUDENT_ID)
print("OpenMP:", nb.threading_layer())
print("CPU cores:", os.cpu_count())
print("N:", N_T1)
print("Bins:", BINS_T1)

set_num_threads(1)
reference_hist, reference_sums = buggy_hist_omp(
    data_t1, weights_t1, BINS_T1
)

set_num_threads(8)

# Warm-up
buggy_hist_omp(data_t1, weights_t1, BINS_T1)

lost_counts = []
max_discrepancies = []

for run in range(10):
    hist, sums = buggy_hist_omp(
        data_t1, weights_t1, BINS_T1
    )

    lost = int(N_T1 - np.sum(hist))
    discrepancy = int(
        np.max(np.abs(hist - reference_hist))
    )

    lost_counts.append(lost)
    max_discrepancies.append(discrepancy)

    print(
        f"Run {run + 1}: "
        f"lost counts={lost}, "
        f"max discrepancy={discrepancy}"
    )

print("Total lost counts:", lost_counts)
print("Maximum discrepancy:", max(max_discrepancies))


# TASK 1D: Safe implementation across thread counts
print("\n========== SAFE HISTOGRAM ==========")

safe_results = {}

for threads in (1, 2, 4, 8):
    set_num_threads(threads)

    start = time.perf_counter()
    hist, sums, hits = safe_hist_omp(
        data_t1, weights_t1, BINS_T1
    )
    elapsed = time.perf_counter() - start

    assert int(np.sum(hist)) == N_T1
    assert np.allclose(
        sums, reference_sums, rtol=1e-10, atol=1e-8
    )

    safe_results[threads] = (hist.copy(), sums.copy())

    print(f"\nThreads: {threads}")
    print("Elapsed seconds:", round(elapsed, 4))
    print("Histogram total:", int(np.sum(hist)))
    print("Worker hits:", hits)
    print("Active workers:", int(np.count_nonzero(hits)))


# Verify exact integer histogram equality
base_hist = safe_results[1][0]

for threads in (2, 4, 8):
    assert np.array_equal(
        base_hist, safe_results[threads][0]
    )

print("\nInteger histograms match across thread counts.")


# Diagnosis
DIAGNOSIS_T1 = """
The race condition occurs because multiple OpenMP threads can update
the same histogram bin at the same time. An increment is a read-modify-write
operation, so simultaneous updates can overwrite one another and cause
lost counts. The safe implementation gives each worker a private histogram
and weighted-sum row, avoiding concurrent writes to the same bin. After
the parallel loop, the private rows are merged in a fixed thread order.
Floating-point addition is not associative: (a+b)+c may differ from
a+(b+c) because of finite precision. Therefore, changing the grouping
or order of additions can produce small numerical differences even
when integer histogram counts are exact.
"""

assert len(DIAGNOSIS_T1.strip()) >= 80

print("\n========== TASK 1 COMPLETE ==========")
print("Diagnosis length:", len(DIAGNOSIS_T1))
print("OpenMP layer:", nb.threading_layer())


# ============================================================
# TASK 2: ELIMINATING CACHE-LINE FALSE SHARING
# ============================================================

print("\n========== TASK 2: FALSE SHARING ==========")

ITERS_T2 = 35_000_000 + (STUDENT_ID % 503) * 10_000
PAD_STRIDE = 8 + (STUDENT_ID % 5) * 8

print("Iterations:", ITERS_T2)
print("Padding stride:", PAD_STRIDE)


@njit(parallel=True)
def unpadded_state_omp(iters, seed_val):
    n_threads = get_num_threads()
    state = np.zeros(n_threads, dtype=np.int64)

    for t in prange(n_threads):
        tid = get_thread_id()
        x = np.int64(seed_val + tid * 1315423911)

        for step in range(iters):
            x = (
                x * np.int64(6364136223846793005)
                + np.int64(1442695040888963407)
            ) & np.int64(0x7FFFFFFFFFFFFFFF)

            state[tid] ^= (x >> 17)

    return state


@njit(parallel=True)
def padded_state_omp(iters, seed_val, pad_stride):
    n_threads = get_num_threads()

    padded_state = np.zeros(
        (n_threads, pad_stride), dtype=np.int64
    )

    for t in prange(n_threads):
        tid = get_thread_id()
        x = np.int64(seed_val + tid * 1315423911)

        for step in range(iters):
            x = (
                x * np.int64(6364136223846793005)
                + np.int64(1442695040888963407)
            ) & np.int64(0x7FFFFFFFFFFFFFFF)

            padded_state[tid, 0] ^= (x >> 17)

    return padded_state


# Warm-up both kernels
set_num_threads(1)
unpadded_state_omp(10, STUDENT_ID)
padded_state_omp(10, STUDENT_ID, PAD_STRIDE)

task2_results = {}

for threads in (1, 2, 4, 8):
    set_num_threads(threads)

    # Warm-up
    unpadded_state_omp(100, STUDENT_ID)
    padded_state_omp(100, STUDENT_ID, PAD_STRIDE)

    # Benchmark unpadded
    start = time.perf_counter()
    unpadded = unpadded_state_omp(ITERS_T2, STUDENT_ID)
    unpadded_time = time.perf_counter() - start

    # Benchmark padded
    start = time.perf_counter()
    padded = padded_state_omp(
        ITERS_T2, STUDENT_ID, PAD_STRIDE
    )
    padded_time = time.perf_counter() - start

    padded_values = padded[:, 0]

    # Exact verification
    assert np.array_equal(unpadded, padded_values)

    task2_results[threads] = {
        "unpadded": unpadded_time,
        "padded": padded_time,
    }

    print(f"\nThreads: {threads}")
    print("Unpadded time:", round(unpadded_time, 4), "seconds")
    print("Padded time:", round(padded_time, 4), "seconds")
    print("Results identical: True")


speedup_t2 = (
    task2_results[8]["unpadded"]
    / task2_results[8]["padded"]
)

print("\n8-thread padding speedup:", round(speedup_t2, 4), "x")


DIAGNOSIS_T2 = """
False sharing occurs when different OpenMP threads update separate
variables that occupy the same cache line. Even though the variables
are logically independent, the cache-coherence protocol must transfer
ownership of the shared cache line between processor cores. This causes
repeated invalidations and reduces performance. The padded implementation
places each thread's active state in a separate cache line using a
stride of at least eight int64 elements. This reduces unnecessary
cache-line sharing while preserving the same calculations and results.
"""

assert len(DIAGNOSIS_T2.strip()) >= 80

print("Diagnosis length:", len(DIAGNOSIS_T2))
print("Task 2 verification completed.")

# ========== TASK 3: IRREGULAR WORKLOAD SKEW ==========

import math

ROWS_T3 = 12_304
SKEW_MOD = 40
CHUNK_T3 = 16
PAD_STRIDE_T3 = 8

rng_t3 = np.random.default_rng(STUDENT_ID)
x_t3 = rng_t3.uniform(-2.0, 2.0, ROWS_T3).astype(np.float64)

work_units_t3 = np.array(
    [40 + ((r * 7919 + STUDENT_ID) % SKEW_MOD) ** 2
     for r in range(ROWS_T3)],
    dtype=np.int64
)


@njit(parallel=True)
def static_skew_omp(x, work_units, pad_stride):
    n_threads = get_num_threads()
    out = np.zeros(x.shape[0], dtype=np.float64)
    ops = np.zeros((n_threads, pad_stride), dtype=np.int64)

    for r in prange(x.shape[0]):
        tid = get_thread_id()
        total = 0.0
        count = work_units[r]

        for k in range(count):
            value = x[r] + k * 0.0001
            total += math.sin(value) * math.cos(value) + math.sqrt(abs(value) + 1.0)

        out[r] = total
        ops[tid, 0] += count

    return out, ops


@njit(parallel=True)
def balanced_skew_omp(x, work_units, chunk_size, pad_stride):
    n_threads = get_num_threads()
    n_rows = x.shape[0]

    out = np.zeros(n_rows, dtype=np.float64)
    ops = np.zeros((n_threads, pad_stride), dtype=np.int64)

    # Each worker receives interleaved rows.
    # This balances the deterministic workload without shared writes.
    for worker in prange(n_threads):
        tid = get_thread_id()
        local_ops = 0

        for start in range(worker * chunk_size, n_rows, n_threads * chunk_size):
            end = min(start + chunk_size, n_rows)

            for r in range(start, end):
                total = 0.0
                count = work_units[r]

                for k in range(count):
                    value = x[r] + k * 0.0001
                    total += math.sin(value) * math.cos(value) + math.sqrt(abs(value) + 1.0)

                out[r] = total
                local_ops += count

        ops[tid, 0] = local_ops

    return out, ops


print("\n========== TASK 3: WORKLOAD SKEW ==========")

T3_RESULTS = {}
out_t3 = None

for threads in (1, 2, 4, 8):
    set_num_threads(threads)

    # Warm-up
    static_skew_omp(x_t3, work_units_t3, PAD_STRIDE_T3)
    balanced_skew_omp(x_t3, work_units_t3, CHUNK_T3, PAD_STRIDE_T3)

    start = time.perf_counter()
    static_out, static_ops = static_skew_omp(
        x_t3, work_units_t3, PAD_STRIDE_T3
    )
    static_time = time.perf_counter() - start

    start = time.perf_counter()
    balanced_out, balanced_ops = balanced_skew_omp(
        x_t3, work_units_t3, CHUNK_T3, PAD_STRIDE_T3
    )
    balanced_time = time.perf_counter() - start

    static_active = static_ops[:, 0][static_ops[:, 0] > 0]
    balanced_active = balanced_ops[:, 0][balanced_ops[:, 0] > 0]

    static_imbalance = (
        float(np.max(static_active)) / float(np.min(static_active))
    )
    balanced_imbalance = (
        float(np.max(balanced_active)) / float(np.min(balanced_active))
    )

    difference = float(np.max(np.abs(static_out - balanced_out)))

    print(f"\nThreads: {threads}")
    print(f"Static time: {static_time:.6f} seconds")
    print(f"Static imbalance: {static_imbalance:.4f}x")
    print(f"Balanced time: {balanced_time:.6f} seconds")
    print(f"Balanced imbalance: {balanced_imbalance:.4f}x")
    print(f"Maximum output difference: {difference:.3e}")

    assert difference < 1e-11, "Task 3 output mismatch!"

    T3_RESULTS[threads] = {
        "static_time": static_time,
        "balanced_time": balanced_time,
        "static_imbalance": static_imbalance,
        "balanced_imbalance": balanced_imbalance,
    }

    if threads == 8:
        out_t3 = balanced_out.copy()
        assert balanced_imbalance < 1.15, (
            f"Load imbalance too high: {balanced_imbalance:.4f}"
        )

DIAGNOSIS_T3 = (
    "Static scheduling assigns contiguous row blocks to threads, but the "
    "computational cost of each row varies quadratically with its workload "
    "factor. As a result, some threads process much more work and become "
    "stragglers while other threads wait at the parallel loop barrier. "
    "The balanced scheduler distributes interleaved row chunks across "
    "workers, spreading expensive and inexpensive rows more evenly. "
    "Each worker writes to distinct output rows and maintains its own "
    "padded operation counter, avoiding data races. Both approaches "
    "compute the same row formula, so their outputs agree within tolerance."
)

print("\nTask 3 verification completed.")
print("Diagnosis length:", len(DIAGNOSIS_T3))


# ============================================================
# TASK 4: RED-BLACK SOR FOR ANISOTROPIC LAPLACE PDE
# ============================================================

print("\n========== TASK 4: RED-BLACK SOR ==========")

GRID_H = 384 + (STUDENT_ID % 4) * 32
GRID_W = 512 + (STUDENT_ID % 5) * 32
OMEGA_SOR = np.float64(1.72 + (STUDENT_ID % 11) * 0.015)
SWEEPS_T4 = 600

print("Grid:", GRID_H, "x", GRID_W)
print("Omega:", OMEGA_SOR)
print("Red-Black iterations:", SWEEPS_T4)


def initialize_grid_t4():
    U = np.zeros((GRID_H, GRID_W), dtype=np.float64)

    U[0, :] = 100.0
    U[-1, :] = -50.0
    U[:, 0] = 25.0 * np.sin(np.linspace(0, np.pi, GRID_H))
    U[:, -1] = 75.0 * np.cos(np.linspace(0, np.pi / 2, GRID_H))

    return U


@njit(parallel=True)
def red_black_sor_omp(U, omega, sweeps, pad_stride):
    height, width = U.shape
    n_threads = get_num_threads()

    # One padded maximum-delta slot per OpenMP worker.
    thread_max = np.zeros((n_threads, pad_stride), dtype=np.float64)

    for iteration in range(sweeps):

        for tid in range(n_threads):
            thread_max[tid, 0] = 0.0

        # RED sweep.
        # The end of this prange provides the barrier before BLACK.
        for r in prange(1, height - 1):
            tid = get_thread_id()

            for c in range(1, width - 1):
                if (r + c) % 2 == 0:
                    old_value = U[r, c]

                    new_value = (
                        (1.0 - omega) * old_value
                        + 0.25 * omega * (
                            U[r - 1, c]
                            + U[r + 1, c]
                            + U[r, c - 1]
                            + U[r, c + 1]
                        )
                    )

                    U[r, c] = new_value
                    delta = abs(new_value - old_value)

                    if delta > thread_max[tid, 0]:
                        thread_max[tid, 0] = delta

        # BLACK sweep.
        # RED values are now updated and visible after the barrier.
        for r in prange(1, height - 1):
            tid = get_thread_id()

            for c in range(1, width - 1):
                if (r + c) % 2 == 1:
                    old_value = U[r, c]

                    new_value = (
                        (1.0 - omega) * old_value
                        + 0.25 * omega * (
                            U[r - 1, c]
                            + U[r + 1, c]
                            + U[r, c - 1]
                            + U[r, c + 1]
                        )
                    )

                    U[r, c] = new_value
                    delta = abs(new_value - old_value)

                    if delta > thread_max[tid, 0]:
                        thread_max[tid, 0] = delta

        # Reduction after both color sweeps.
        residual = 0.0
        for tid in range(n_threads):
            if thread_max[tid, 0] > residual:
                residual = thread_max[tid, 0]

    return U, residual


initial_grid_t4 = initialize_grid_t4()
T4_RESULTS = {}
grid_reference_t4 = None
grid_t4 = None

for threads in (1, 2, 4, 8):
    set_num_threads(threads)

    # Warm-up / compilation
    warm_grid = initial_grid_t4.copy()
    red_black_sor_omp(warm_grid, OMEGA_SOR, 2, PAD_STRIDE)

    test_grid = initial_grid_t4.copy()

    start = time.perf_counter()
    result_grid, residual = red_black_sor_omp(
        test_grid, OMEGA_SOR, SWEEPS_T4, PAD_STRIDE
    )
    elapsed = time.perf_counter() - start

    if threads == 1:
        grid_reference_t4 = result_grid.copy()

    difference = float(
        np.max(np.abs(result_grid - grid_reference_t4))
    ) if grid_reference_t4 is not None else 0.0

    T4_RESULTS[threads] = {
        "time": elapsed,
        "residual": residual,
        "difference": difference,
    }

    if threads == 8:
        grid_t4 = result_grid.copy()

    print(f"\nThreads: {threads}")
    print(f"Elapsed time: {elapsed:.4f} seconds")
    print(f"Final residual: {residual:.6e}")

    if threads == 1:
        print("Reference solution created.")
    else:
        print(f"Maximum difference from 1-thread result: {difference:.3e}")
        assert difference < 1e-9, "Task 4 numerical mismatch!"

print("\nTask 4 speedups:")

baseline_t4 = T4_RESULTS[1]["time"]

for threads in (1, 2, 4, 8):
    speedup = baseline_t4 / T4_RESULTS[threads]["time"]
    print(f"{threads} threads: {speedup:.4f}x")

DIAGNOSIS_T4 = """
Red-Black SOR updates the grid in two color phases. During the red
phase, cells with even row-plus-column parity are updated in parallel.
The black phase starts after the implicit OpenMP barrier and uses the
new red values. Cells of the same color are not direct neighbors, so
their updates can safely run concurrently. Each worker maintains a
padded maximum-delta value, which is reduced after both phases to
calculate the iteration residual without a data race.
"""

assert len(DIAGNOSIS_T4.strip()) >= 80
print("Task 4 verification completed.")


# ============================================================
# FINAL VERIFICATION BUNDLE
# ============================================================

print("\n========== FINAL VERIFICATION ==========")

set_num_threads(8 if (os.cpu_count() or 1) >= 8 else (os.cpu_count() or 1))

for idx, diag in enumerate(
    [DIAGNOSIS_T1, DIAGNOSIS_T2, DIAGNOSIS_T3], start=1
):
    assert isinstance(diag, str) and len(diag.strip()) >= 80, (
        f"Complete DIAGNOSIS_T{idx}!"
    )

hist_t1 = base_hist
wsums_t1 = reference_sums
state_t2 = padded[:, 0]

assert grid_t4 is not None

checksum_blob = (
    f"{STUDENT_ID}|"
    f"{int(np.sum(hist_t1))}|{float(np.sum(wsums_t1)):.4f}|"
    f"{int(np.bitwise_xor.reduce(state_t2))}|"
    f"{float(np.sum(out_t3)):.6f}|"
    f"{float(np.sum(grid_t4)):.6f}"
)

lab_digest = hashlib.sha256(checksum_blob.encode()).hexdigest()[:20].upper()

bundle = {
    "instructor": "Instructor - Sufyan bin Uzayr",
    "student_name": STUDENT_NAME,
    "student_id": STUDENT_ID,
    "omp_layer": nb.threading_layer(),
    "cpu_cores": os.cpu_count(),
    "verification_digest": lab_digest,
}

print("=== OPENMP PYTHON LAB VERIFICATION BUNDLE ===")
print(json.dumps(bundle, indent=2))

print("\nALL AVAILABLE TASKS COMPLETED.")
