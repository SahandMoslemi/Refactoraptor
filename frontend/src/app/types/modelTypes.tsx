// app/types/modelTypes.tsx
// Type definitions for models

export type Model = string;

export interface ModelInfo {
    id: string;
    name: string;
    description: string;
}

export interface ModelDropdownProps {
    selectedModel: Model | null;
    setSelectedModel: (model: Model | null) => void;
    models?: string[];
}

// Default model information with descriptions
export const DEFAULT_MODELS: string[] = ["deepseek-1", "llama3.1", "qwen2.5"];

export const MODEL_INFO_MAP: Record<string, ModelInfo> = {
    "deepseek-1": {
        id: "deepseek-1",
        name: "DeepSeek-1",
        description: "Most accurate model with SOLID principles expertise",
    },
    "llama3.1": {
        id: "llama3.1",
        name: "Llama 3.1",
        description: "Fast, reliable code optimizations",
    },
    "qwen2.5": {
        id: "qwen2.5",
        name: "Qwen 2.5",
        description: "Best for complex refactoring tasks",
    }
};