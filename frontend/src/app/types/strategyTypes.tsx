// app/types/modelTypes.tsx
// Type definitions for models

export type PromptStrategy = string;

export interface StrategyInfo {
    id: string;
    name: string;
    description: string;
}

export interface PromptStrategyDropdownProps {
    selectedPrompt: PromptStrategy | null;
    setStrategy: (strategy: PromptStrategy | null) => void;
    promptStrategies?: string[];
}

// Default model information with descriptions
export const DEFAULT_STRATS: string[] = ["DEFAULT"];

export const STRAT_INFO_MAP: Record<string, StrategyInfo> = {
    
};