// api/modelService.tsx
// Service for handling model-related API calls

export interface ModelItem {
    name: string;
    [key: string]: unknown;
}

export interface ModelsResponse {
    models?: ModelItem[];
    names?: string[];
    [key: string]: unknown;
}

/**
 * Fetches available models from the API
 * @param isOnline Whether to fetch online or local models
 * @returns Promise with an array of model names
 */
export async function fetchModels(isOnline: boolean = true): Promise<string[]> {
    try {
        // Use the appropriate endpoint based on the isOnline flag
        const endpoint = isOnline ? 'http://localhost:8080/models-online' : 'http://localhost:8080/models';
        const response = await fetch(endpoint);

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        return parseModelsResponse(data);
    } catch (error) {
        console.error("Error fetching models:", error);
        throw error;
    }
}

/**
 * Parses the models response from the API into a simple string array
 * @param data API response data
 * @returns Array of model names
 */
function parseModelsResponse(data: unknown): string[] {
    let modelNames: string[] = [];

    if (Array.isArray(data)) {
        modelNames = data.map((item: ModelItem) => item.name);
    } else if (data && typeof data === 'object' && Array.isArray((data as ModelsResponse).models)) {
        const typedData = data as ModelsResponse;
        modelNames = typedData.models?.map((item: ModelItem) => item.name) || [];
    } else if (data && typeof data === 'object') {
        const typedData = data as ModelsResponse;
        if (typedData.names && Array.isArray(typedData.names)) {
            modelNames = typedData.names;
        } else if (typedData.models && Array.isArray(typedData.models)) {
            modelNames = typedData.models as unknown as string[];
        } else {
            modelNames = Object.keys(typedData)
                .filter(key => typeof typedData[key] === 'string' || typeof typedData[key] === 'object')
                .map(key => {
                    if (typeof typedData[key] === 'string') return typedData[key] as string;
                    const itemObj = typedData[key] as { name?: string };
                    if (itemObj && itemObj.name) return itemObj.name;
                    return key;
                });
        }
    }

    return modelNames;
}