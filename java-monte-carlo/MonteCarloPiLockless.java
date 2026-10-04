import java.util.Random;

public class MonteCarloPiLockless {

    static final long TOTAL_POINTS = 10_000_000;
    static final int NUM_THREADS = 4;

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

    public static void main(String[] args) throws InterruptedException {

        MonteCarloWorker[] threads =
                new MonteCarloWorker[NUM_THREADS];

        long pointsPerThread = TOTAL_POINTS / NUM_THREADS;

        long start = System.nanoTime();

        for (int i = 0; i < NUM_THREADS; i++) {
            threads[i] = new MonteCarloWorker(pointsPerThread);
            threads[i].start();
        }

        long totalInside = 0;

        for (MonteCarloWorker thread : threads) {
            thread.join();
            totalInside += thread.getLocalInside();
        }

        long end = System.nanoTime();

        double pi = 4.0 * totalInside / TOTAL_POINTS;
        double timeSeconds =
                (end - start) / 1_000_000_000.0;

        System.out.println("Threads: " + NUM_THREADS);
        System.out.println("Total points: " + TOTAL_POINTS);
        System.out.println("Points inside circle: " + totalInside);
        System.out.println("Estimated Pi: " + pi);
        System.out.printf(
                "Execution time: %.4f seconds%n",
                timeSeconds
        );
    }
}
