public class Task3RaceCondition {

    static long counter = 0;

    static final int THREADS = 10;
    static final int INCREMENTS = 1_000_000;

    public static void main(String[] args) throws InterruptedException {

        long expected = (long) THREADS * INCREMENTS;

        System.out.println("Task 3 - Unsynchronized Shared Counter");
        System.out.println("Threads: " + THREADS);
        System.out.println("Increments per thread: " + INCREMENTS);
        System.out.println("Expected value: " + expected);
        System.out.println();

        for (int run = 1; run <= 10; run++) {

            counter = 0;
            Thread[] threads = new Thread[THREADS];

            long start = System.nanoTime();

            for (int t = 0; t < THREADS; t++) {
                threads[t] = new Thread(() -> {
                    for (int i = 0; i < INCREMENTS; i++) {
                        counter++;
                    }
                });

                threads[t].start();
            }

            for (Thread thread : threads) {
                thread.join();
            }

            double seconds =
                    (System.nanoTime() - start) / 1_000_000_000.0;

            long error = expected - counter;

            System.out.printf(
                    "Run %2d | Actual: %d | Lost: %d | Time: %.4f s%n",
                    run, counter, error, seconds
            );
        }
    }
}
