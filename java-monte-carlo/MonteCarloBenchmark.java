import java.util.Random;

public class MonteCarloBenchmark {

    static final long TOTAL_POINTS = 10_000_000;
    static final int[] THREAD_COUNTS = {1, 2, 4, 8, 16, 32};

    static class MonteCarloWorker extends Thread {
        private final long numberOfPoints;
        private long localInside = 0;

        MonteCarloWorker(long numberOfPoints) {
            this.numberOfPoints = numberOfPoints;
        }

        @Override
        public void run() {
            Random random = new Random();

            for (long i = 0; i < numberOfPoints; i++) {
                double x = random.nextDouble();
                double y = random.nextDouble();

                if (x * x + y * y <= 1.0) {
                    localInside++;
                }
            }
        }

        public long getLocalInside() {
            return localInside;
        }
    }

    static void runBenchmark(int numThreads)
            throws InterruptedException {

        MonteCarloWorker[] threads =
                new MonteCarloWorker[numThreads];

        long pointsPerThread = TOTAL_POINTS / numThreads;
        long remainder = TOTAL_POINTS % numThreads;

        long start = System.nanoTime();

        for (int i = 0; i < numThreads; i++) {

            long points = pointsPerThread;

            if (i < remainder) {
                points++;
            }

            threads[i] = new MonteCarloWorker(points);
            threads[i].start();
        }

        long totalInside = 0;

        for (MonteCarloWorker thread : threads) {
            thread.join();
            totalInside += thread.getLocalInside();
        }

        long end = System.nanoTime();

        double pi = 4.0 * totalInside / TOTAL_POINTS;
        double time =
                (end - start) / 1_000_000_000.0;

        System.out.printf(
                "%d\t%.7f\t%.4f%n",
                numThreads,
                pi,
                time
        );
    }

    public static void main(String[] args)
            throws InterruptedException {

        System.out.println("Monte Carlo Pi Benchmark");
        System.out.println("Total points: " + TOTAL_POINTS);
        System.out.println();
        System.out.println("Threads\tPi\t\tTime(s)");

        for (int threads : THREAD_COUNTS) {
            runBenchmark(threads);
        }
    }
}
