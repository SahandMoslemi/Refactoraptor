export async function fetchPromptStrategies(): Promise<string[]> {
    try {
        const response = await fetch('http://localhost:8080/strategies');

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        return processStrategies(data)
    } catch (error) {
        console.error("Error fetching models:", error);
        throw error;
    }
}

function processStrategies(strategies: string[]): string[] {
    return strategies
        .map(strategy => {
            if (strategy.length === 0) return strategy;
            return strategy.charAt(0).toUpperCase() + strategy.slice(1).toLowerCase();
        })
        .sort((a, b) => a.localeCompare(b));
}