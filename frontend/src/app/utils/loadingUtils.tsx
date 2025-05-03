// app/utils/loadingUtils.tsx
// Utility functions for loading states and animations

import { useEffect, useState, useCallback } from 'react';

/**
 * Custom hook for managing loading dots animation
 * @param interval The interval in ms for dots animation
 * @returns Current dots string
 */
export function useLoadingDots(interval = 500): string {
    const [dots, setDots] = useState("");

    useEffect(() => {
        const dotsInterval = setInterval(() => {
            setDots((prev) => (prev.length >= 3 ? "" : prev + "."));
        }, interval);

        return () => clearInterval(dotsInterval);
    }, [interval]);

    return dots;
}

/**
 * Custom hook for managing process status
 * @param initialStatus Initial status message
 * @returns [status, setStatus] tuple
 */
export function useProcessStatus(initialStatus = "Initializing..."): [string, (status: string) => void] {
    const [status, setStatus] = useState(initialStatus);
    return [status, setStatus];
}