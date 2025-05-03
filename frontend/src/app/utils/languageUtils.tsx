// utils/languageUtils.tsx
// Utility functions for language-related operations

export type Language = "java" | "kotlin" | "c#" | "python";
export type PromptType = "basic" | "example-based" | "solid-principles";

// Available language options
export const LANGUAGES: Language[] = ["java", "kotlin", "c#", "python"];

// Available prompt types
export const PROMPT_TYPES: PromptType[] = ["basic", "example-based", "solid-principles"];

/**
 * Gets the appropriate file extension for a given language
 * @param lang The programming language
 * @returns The file extension including the dot (e.g., ".java")
 */
export function getFileExtension(lang: string | null): string {
    if (!lang) return "";

    const extensions: Record<string, string> = {
        java: ".java",
        kotlin: ".kt",
        "c#": ".cs",
        python: ".py",
    };

    return extensions[lang] || "";
}

/**
 * Gets a human-readable label for a prompt type
 * @param type The prompt type
 * @returns A user-friendly label
 */
export function getPromptTypeLabel(type: string): string {
    switch (type) {
        case "basic":
            return "Basic prompt";
        case "example-based":
            return "Example-based prompt";
        case "solid-principles":
            return "SOLID principles improvement";
        default:
            return type;
    }
}