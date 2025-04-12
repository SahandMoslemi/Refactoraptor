"use client";

import { useState, useRef, useEffect } from "react";
import Image from "next/image";

type Model = "deepseek-1" | "llama3.1" | "qwen2.5";

interface ModelDropdownProps {
  selectedModel: Model | null;
  setSelectedModel: (model: Model | null) => void;
}

const ModelDropdown = ({
  selectedModel,
  setSelectedModel,
}: ModelDropdownProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const models: { id: Model; name: string; description: string }[] = [
    {
      id: "deepseek-1",
      name: "DeepSeek-1",
      description: "Most accurate model with SOLID principles expertise",
    },
    {
      id: "llama3.1",
      name: "Llama 3.1",
      description: "Fast, reliable code optimizations",
    },
    {
      id: "qwen2.5",
      name: "Qwen 2.5",
      description: "Best for complex refactoring tasks",
    },
  ];

  // Handle clicking outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full bg-[#4c5944] rounded px-3 py-2 text-white text-left flex justify-between items-center focus:outline-none focus:ring-1 focus:ring-[#8ea382]"
      >
        <span>
          {selectedModel
            ? models.find((m) => m.id === selectedModel)?.name
            : "Select model"}
        </span>
        <svg
          className={`w-4 h-4 transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-[#4c5944] rounded shadow-lg">
          {models.map((model) => (
            <div
              key={model.id}
              className="px-3 py-2 hover:bg-[#3d4937] cursor-pointer border-b border-[#5a6a50] last:border-b-0"
              onClick={() => {
                setSelectedModel(model.id);
                setIsOpen(false);
              }}
            >
              <div className="font-medium">{model.name}</div>
              <div className="text-xs text-gray-300/70">
                {model.description}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ModelDropdown;
