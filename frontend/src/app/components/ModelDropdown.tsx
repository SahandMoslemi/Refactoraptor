"use client";

import { useState, useRef, useEffect } from "react";

type Model = "deepseek-1" | "llama3.1" | "qwen2.5";

interface ModelDropdownProps {
    selectedModel: Model | null;
    setSelectedModel: (model: Model) => void;
}

const ModelDropdown = ({ selectedModel, setSelectedModel }: ModelDropdownProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    const models: Model[] = ["deepseek-1", "llama3.1", "qwen2.5"];

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    return (
        <div className="relative w-full" ref={dropdownRef}>
    <button
        onClick={() => setIsOpen(!isOpen)}
    className="w-full bg-[#4c5944] rounded px-3 py-2 text-white text-left flex justify-between items-center"
        >
        <span>{selectedModel || "Select model"}</span>
    <svg
    className={`w-4 h-4 transition-transform ${isOpen ? "transform rotate-180" : ""}`}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
    >
    <path
        strokeLinecap="round"
    strokeLinejoin="round"
    strokeWidth="2"
    d="M19 9l-7 7-7-7"
        ></path>
        </svg>
        </button>

    {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-[#4c5944] rounded shadow-lg">
            {models.map((model) => (
                    <div
                        key={model}
                className="px-3 py-2 hover:bg-[#5c6b51] cursor-pointer"
                onClick={() => {
        setSelectedModel(model);
        setIsOpen(false);
    }}
    >
        {model}
        </div>
    ))}
        </div>
    )}
    </div>
);
};

export default ModelDropdown;