"use client";

import { useState } from "react";
import ModelDropdown from "./ModelDropdown";

type Language = "java" | "kotlin" | "c#" | "python";
type Model = "deepseek-1" | "llama3.1" | "qwen2.5";
type PromptType = "basic" | "example-based" | "solid-principles";

interface ControlPanelProps {
    fileName: string;
    setFileName: (name: string) => void;
    language: string | null;
    setLanguage: (lang: string | null) => void;
    model: string | null;
    setModel: (model: string | null) => void;
    promptType: string;
    setPromptType: (type: string) => void;
    onRefactor: () => void;
}

const ControlPanel = ({
                          fileName,
                          setFileName,
                          language,
                          setLanguage,
                          model,
                          setModel,
                          promptType,
                          setPromptType,
                          onRefactor
                      }: ControlPanelProps) => {
    // Available options
    const languages: Language[] = ["java", "kotlin", "c#", "python"];
    const models: Model[] = ["deepseek-1", "llama3.1", "qwen2.5"];
    const promptTypes: PromptType[] = ["basic", "example-based", "solid-principles"];

    // Handle form submission
    const handleRefactor = () => {
        onRefactor();
    };

    return (
        <div className="bg-[#5a6a50]/90 h-full w-full p-4 text-white overflow-y-auto">
            <h2 className="text-xl font-medium mb-4 md:mb-6">Refactor Settings</h2>

            {/* File Name */}
            <div className="mb-4">
                <label className="block text-sm font-medium mb-1">File Name</label>
                <input
                    type="text"
                    placeholder="Enter file name"
                    className="w-full bg-[#4c5944] rounded px-3 py-2 text-white placeholder:text-gray-300/50 focus:outline-none focus:ring-1 focus:ring-[#8ea382]"
                    value={fileName}
                    onChange={(e) => setFileName(e.target.value)}
                />
            </div>

            {/* Language Selection */}
            <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Language</label>
                <div className="grid grid-cols-2 gap-2">
                    {languages.map((lang) => (
                        <div key={lang} className="flex items-center">
                            <input
                                type="radio"
                                id={`lang-${lang}`}
                                name="language"
                                className="mr-2 accent-[#8ea382]"
                                checked={language === lang}
                                onChange={() => setLanguage(lang)}
                            />
                            <label htmlFor={`lang-${lang}`} className="text-sm cursor-pointer">
                                {lang.charAt(0).toUpperCase() + lang.slice(1)}
                            </label>
                        </div>
                    ))}
                </div>
            </div>

            {/* Model Selection - Now as Dropdown */}
            <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Model</label>
                <ModelDropdown
                    selectedModel={model as Model | null}
                    setSelectedModel={(selectedModel) => setModel(selectedModel)}
                />
            </div>

            {/* Prompt Type Selection */}
            <div className="mb-6">
                <label className="block text-sm font-medium mb-1">Prompt Type</label>
                <div className="space-y-1">
                    {promptTypes.map((type) => (
                        <div key={type} className="flex items-center">
                            <input
                                type="radio"
                                id={`prompt-${type}`}
                                name="prompt-type"
                                className="mr-2 accent-[#8ea382]"
                                checked={promptType === type}
                                onChange={() => setPromptType(type)}
                            />
                            <label htmlFor={`prompt-${type}`} className="text-sm cursor-pointer">
                                {type === 'basic' ? 'Basic prompt' :
                                    type === 'example-based' ? 'Example-based prompt' :
                                        'SOLID principles improvement'}
                            </label>
                        </div>
                    ))}
                </div>
            </div>

            {/* Refactor Button */}
            <button
                onClick={handleRefactor}
                className="w-full bg-[#3d4937] hover:bg-[#4c5944] py-3 rounded-md transition-colors font-medium"
            >
                Refactor
            </button>

            {/* Note about model capabilities */}
            <div className="mt-4 text-xs text-gray-300/70 text-center">
                Based on the model you choose, the refactoraptor can make mistakes.
            </div>
        </div>
    );
};

export default ControlPanel;