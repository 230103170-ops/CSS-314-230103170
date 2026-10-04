"""Run in a clean venv: python openmp_lab.py. --quick is validation only."""
import argparse
import csv
import platform
import subprocess
import time
from pathlib import Path
import numpy as np
import numba
from numba import njit, prange
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

@njit(parallel=True)
def monte_carlo_pi(n):
    inside = 0
    for i in prange(n):
        x, y = np.random.random(), np.random.random()
        if x*x + y*y <= 1.0:
            inside += 1
    return 4.0 * inside / n

@njit(parallel=True)
def mandelbrot(h, w, max_iter, columns):
    img = np.zeros((h, w), dtype=np.int32)
    for outer in prange(w if columns else h):
        for inner in range(h if columns else w):
            r, c = (inner, outer) if columns else (outer, inner)
            cx, cy = -2.0 + c/w*2.5, -1.2 + r/h*2.4
            zr, zi, it = 0.0, 0.0, 0
            while zr*zr + zi*zi <= 4.0 and it < max_iter:
                nr = zr*zr - zi*zi + cx
                zi = 2.0*zr*zi + cy
                zr = nr
                it += 1
            img[r, c] = it
    return img

@njit(parallel=True)
def heat_step(u, v, alpha):
    rows, cols = u.shape
    for i in prange(1, rows-1):
        for j in range(1, cols-1):
            v[i,j] = u[i,j] + alpha*(u[i+1,j]+u[i-1,j]+u[i,j+1]+u[i,j-1]-4*u[i,j])

def arrays(n, dtype):
    u = np.zeros((n,n), dtype=dtype)
    v = np.zeros_like(u)
    for a in (u,v):
        a[0,:] = 100
        a[:,0] = 100
    return u,v

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true', help='Small validation workload; NOT submission results')
    parser.add_argument('--repeats', type=int, default=3)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error('--repeats must be positive')
    out = Path('openmp_results_quick' if args.quick else 'openmp_results')
    out.mkdir(exist_ok=True)
    maximum = numba.config.NUMBA_NUM_THREADS
    counts = sorted({t for t in (1,2,4,8,maximum) if t <= maximum})
    samples, size, iterations, grid, steps = (100000,100,50,100,5) if args.quick else (120000000,2500,1000,1500,300)
    cpu = platform.processor() or platform.machine()
    if platform.system() == 'Darwin':
        try:
            cpu = subprocess.check_output(['sysctl','-n','machdep.cpu.brand_string'], text=True).strip()
        except (OSError, subprocess.CalledProcessError):
            pass
    metadata = f'CPU: {cpu}\nOS: {platform.platform()}\nNumPy: {np.__version__}\nNumba: {numba.__version__}\nMaximum threads: {maximum}\nRepeats: {args.repeats}; reported time: median\nQuick validation: {args.quick}\n'
    numba.set_num_threads(maximum)
    monte_carlo_pi(10000)
    metadata += f'Threading layer: {numba.threading_layer()}\n'
    print(metadata, flush=True)
    (out/'hardware.txt').write_text(metadata)
    records = []
    def record(task, threads, workload, elapsed, speed='', efficiency='', throughput=''):
        row = dict(benchmark=task,threads=threads,workload=workload,time_seconds=elapsed,speedup=speed,efficiency_percent=efficiency,megacells_per_second=throughput)
        records.append(row)
        with (out/'results.csv').open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            writer.writeheader()
            writer.writerows(records)
        print(row, flush=True)
    baseline = None
    for t in counts:
        numba.set_num_threads(t)
        monte_carlo_pi(10000)
        times = []
        for _ in range(args.repeats):
            start = time.perf_counter()
            pi = monte_carlo_pi(samples)
            times.append(time.perf_counter()-start)
        elapsed = float(np.median(times))
        if t == 1:
            baseline = elapsed
        record('Monte Carlo',t,samples,elapsed,baseline/elapsed,100*baseline/elapsed/t)
        print(f'Pi estimate: {pi:.6f}', flush=True)
    numba.set_num_threads(maximum)
    for columns in (False,True):
        mandelbrot(100,100,50,columns)
    row_image = None
    for columns in (False,True):
        times = []
        for _ in range(args.repeats):
            start = time.perf_counter()
            image = mandelbrot(size,size,iterations,columns)
            times.append(time.perf_counter()-start)
        elapsed = float(np.median(times))
        record('Mandelbrot columns' if columns else 'Mandelbrot rows',maximum,f'{size}x{size}',elapsed)
        if not columns:
            row_image = image
            plt.figure(figsize=(8,8))
            plt.imshow(image,cmap='magma',origin='lower',extent=[-2,.5,-1.2,1.2])
            plt.title(f'Mandelbrot {size}x{size} (Rows: {elapsed:.2f}s)')
            plt.axis('off')
            plt.savefig(out/'mandelbrot_output.png',dpi=300,bbox_inches='tight')
            plt.close()
        else:
            assert np.array_equal(row_image,image), 'Row/column results differ'
    for dtype in (np.float64,np.float32):
        alpha = dtype(.20)
        u,v = arrays(100,dtype)
        heat_step(u,v,alpha)
        base = None
        for t in counts:
            numba.set_num_threads(t)
            heat_step(u,v,alpha)
            times = []
            for _ in range(args.repeats):
                a,b = arrays(grid,dtype)
                start = time.perf_counter()
                for step in range(steps):
                    heat_step(a,b,alpha)
                    a,b = b,a
                times.append(time.perf_counter()-start)
            elapsed = float(np.median(times))
            if t == 1:
                base = elapsed
            # Lab convention counts the whole grid; only interior cells are updated.
            throughput = grid*grid*steps/elapsed/1e6
            record(f'Heat {np.dtype(dtype).name}',t,f'{grid}x{grid}x{steps}',elapsed,base/elapsed,100*base/elapsed/t,throughput)
    numba.set_num_threads(maximum)
    heat = {r['benchmark']:r for r in records if r['threads']==maximum and r['benchmark'].startswith('Heat')}
    factor = heat['Heat float64']['time_seconds']/heat['Heat float32']['time_seconds']
    print(f'Float64/float32 runtime ratio at max threads: {factor:.3f}x')
    print(f'Saved results in: {out.resolve()}')

if __name__ == '__main__':
    main()
