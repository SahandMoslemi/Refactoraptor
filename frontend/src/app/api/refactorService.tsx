// app/api/refactorService.tsx
// Service for handling code refactoring API calls

export interface CodeChange {
    lineNumber: number;
    explanation: string;
}

export interface RefactoredData {
    originalCode: string;
    refactoredCode: string;
    codeChanges: CodeChange[];
    originalFileName: string;
    executionTime?: string;
    modelUsed?: string;
    language: string | null;
}

interface RefactorRequest {
    model: string;
    strategy: string;
    source: string;
    temperature?: number;
}

interface RefactorResponse {
    response: string;
    total_duration?: number;
    [key: string]: unknown;
}

/**
 * Sends code for refactoring to the backend API
 * @param originalCode The code to refactor
 * @param modelSelected The AI model to use
 * @param promptType The strategy for refactoring
 * @param originalFileName The name of the file
 * @param language The programming language
 * @param temperature The temperature setting for generation
 * @returns Promise with the refactored data
 */
export async function refactorCode(
    originalCode: string,
    modelSelected: string,
    promptType: string,
    originalFileName: string,
    language: string | null,
    temperature: number = 0.0
): Promise<RefactoredData> {
    // Prepare request data
    const requestData: RefactorRequest = {
        model: modelSelected,
        strategy: 'DEFAULT', //promptType.toUpperCase(),
        source: originalCode,
        temperature: temperature
    };

    // Make API request
    const response = await fetch('http://localhost:8080/refactor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    });

    // Handle errors
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to refactor code: ${response.status} ${errorText}`);
    }

    // Parse response
    const data = await response.json() as RefactorResponse;
    const refactoredCode = data.response || '';

    // Format execution time
    let executionTime = "N/A";
    if (data.total_duration) {
        const totalSeconds = Math.floor(data.total_duration as number / 1000000000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        executionTime = minutes > 0
            ? `${minutes} min ${seconds} sec`
            : `${seconds} sec`;
    }

    // Create code changes
    const codeChanges: CodeChange[] = [
        { lineNumber: 1, explanation: `Code refactored according to ${promptType} strategy` }
    ];

    // Return formatted data
    return {
        originalCode,
        refactoredCode,
        codeChanges,
        originalFileName,
        executionTime,
        modelUsed: modelSelected,
        language
    };
}