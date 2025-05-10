export async function fetchPromptStrategies(): Promise<string[]> {
    try {
        const response = await fetch('http://localhost:8080/strategies');

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching models:", error);
        throw error;
    }
}
