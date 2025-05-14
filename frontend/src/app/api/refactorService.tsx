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
    explanation: string;
    violation_type: string;
}

interface RefactorRequest {
    model: string;
    strategy: string;
    source: string;
    temperature?: number;
    language?: string;
}

interface RefactorResponse {
    violation_type: string;
    refactored_code: string;
    explanation: string;
    total_duration: number
}

/**
 * Sends code for refactoring to the backend API
 * @param originalCode The code to refactor
 * @param modelSelected The AI model to use
 * @param promptType The strategy for refactoring
 * @param originalFileName The name of the file
 * @param language The programming language
 * @param temperature The temperature setting for generation
 * @param isOnline Whether to use online or local models
 * @returns Promise with the refactored data
 */
export async function refactorCode(
    originalCode: string,
    modelSelected: string,
    promptType: string,
    originalFileName: string,
    language: string,
    temperature: number = 0.0,
    isOnline: boolean = false
): Promise<RefactoredData> {

    // Prepare request data
    const requestData: RefactorRequest = {
        model: modelSelected,
        strategy: promptType,
        source: originalCode,
        temperature: temperature,
        language: language
    };

    // Choose the appropriate endpoint based on the isOnline flag
    const endpoint = isOnline ? 'http://localhost:8080/refactor-online' : 'http://localhost:8080/refactor';

    // Make API request
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    });

    console.log(response);

    // Handle errors
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to refactor code: ${response.status} ${errorText}`);
    }

    // Parse response
    const data = await response.json() as RefactorResponse;
    console.log(data);

    const refactoredCode = data.refactored_code || '';


    let explanation = data.explanation || '';
    let violation_type = data.violation_type || '';

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
        language,
        explanation,
        violation_type
    };
}