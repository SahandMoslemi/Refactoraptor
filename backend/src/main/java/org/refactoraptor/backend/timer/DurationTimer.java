package org.refactoraptor.backend.timer;

public class DurationTimer {
    private long startTime;
    private long endTime;
    private boolean running;

    public DurationTimer() {
        running = false;
    }

    public void start() {
        startTime = System.nanoTime();
        running = true;
    }

    public void stop() {
        endTime = System.nanoTime();
        running = false;
    }

    public long getElapsedTimeNanos() {
        return running ? System.currentTimeMillis()* 1000000 - startTime : endTime - startTime;
    }

    public boolean isRunning() {
        return running;
    }

    public void reset() {
        startTime = 0;
        endTime = 0;
        running = false;
    }
}

