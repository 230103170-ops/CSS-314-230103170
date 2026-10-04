import java.util.Random;
import java.util.concurrent.atomic.AtomicLong;

public class MonteCarloPiAtomic {

    static final long TOTAL_POINTS = 10_000_000;
    static final int NUM_THREADS = 4;

    static AtomicLong pointsInsideCircle = new AtomicLong(0);

    static class MonteCarloWorker extends Thread {
        private final long numberOfPoints;

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
                    pointsInsideCircle.incrementAndGet();
                }
            }
        }
    }

    public static void main(String[] args) throws InterruptedException {

        Thread[] threads = new Thread[NUM_THREADS];
        long pointsPerThread = TOTAL_POINTS / NUM_THREADS;

        long start = System.nanoTime();

        for (int i = 0; i < NUM_THREADS; i++) {
            threads[i] = new MonteCarloWorker(pointsPerThread);
            threads[i].start();
        }

        for (Thread thread : threads) {
            thread.join();
        }

        long end = System.nanoTime();

        long inside = pointsInsideCircle.get();
        double pi = 4.0 * inside / TOTAL_POINTS;
        double timeSeconds = (end - start) / 1_000_000_000.0;

        System.out.println("Threads: " + NUM_THREADS);
        System.out.println("Total points: " + TOTAL_POINTS);
        System.out.println("Points inside circle: " + inside);
        System.out.println("Estimated Pi: " + pi);
        System.out.printf("Execution time: %.4f seconds%n", timeSeconds);
    }
}
