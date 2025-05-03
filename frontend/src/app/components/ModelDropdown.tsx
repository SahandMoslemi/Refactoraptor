"use client";

import React from "react";
import {
  Model,
  ModelInfo,
  ModelDropdownProps,
  MODEL_INFO_MAP,
  DEFAULT_MODELS
} from "../types/modelTypes";
import { useDropdown } from "../utils/useDropdownUtils";

const ModelDropdown = ({
                         selectedModel,
                         setSelectedModel,
                         models = DEFAULT_MODELS
                       }: ModelDropdownProps) => {
  // Use dropdown utility hook
  const { isOpen, toggleDropdown, dropdownRef, setIsOpen } = useDropdown();

  // Convert models array to ModelInfo array with descriptions when available
  const modelInfoList = models.map(model => {
    if (MODEL_INFO_MAP[model]) {
      return MODEL_INFO_MAP[model];
    } else {
      return {
        id: model,
        name: model,
        description: "External model"
      };
    }
  });

  // Find the name of the selected model
  const getSelectedModelName = () => {
    if (!selectedModel) return "Select model";
    const modelInfo = modelInfoList.find(m => m.id === selectedModel);
    return modelInfo ? modelInfo.name : selectedModel;
  };

  // Handle model selection
  const handleSelectModel = (model: ModelInfo) => {
    setSelectedModel(model.id);
    setIsOpen(false);
  };

  return (
      <div className="relative" ref={dropdownRef}>
        <button
            onClick={toggleDropdown}
            className="w-full bg-[#4c5944] rounded px-3 py-2 text-white text-left flex justify-between items-center focus:outline-none focus:ring-1 focus:ring-[#8ea382]"
        >
          <span>{getSelectedModelName()}</span>
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
              {modelInfoList.map((model) => (
                  <div
                      key={model.id}
                      className="px-3 py-2 hover:bg-[#3d4937] cursor-pointer border-b border-[#5a6a50] last:border-b-0"
                      onClick={() => handleSelectModel(model)}
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