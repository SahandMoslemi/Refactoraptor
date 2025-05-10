"use client";

import { useState, useEffect, useRef } from "react";

import ModelDropdown from "./ModelDropdown";
import { fetchModels } from "../api/modelService";

import { fetchPromptStrategies } from "../api/PromptStrategyService";

import {
  LANGUAGES,
  getFileExtension,
  getPromptTypeLabel,
} from "../utils/languageUtils";


interface ControlPanelProps {
  fileName: string;
  setFileName: (name: string) => void;
  language: string | null;
  setLanguage: (lang: string | null) => void;
  model: string | null;
  setModel: (model: string | null) => void;
  promptStrategy: string;
  setPromptStrategy: (promptStrategy: string) => void;
  temperature: number;
  setTemperature: (temp: number) => void;
  onRefactor: () => void;
  filesUploaded?: boolean;
  isOnline: boolean;
  setIsOnline: (isOnline: boolean) => void;
}

const ControlPanel = ({
  fileName,
  setFileName,
  language,
  setLanguage,
  model,
  setModel,
  promptStrategy,
  setPromptStrategy,
  temperature,
  setTemperature,
  onRefactor,
  filesUploaded = false,
  isOnline,
  setIsOnline,
}: ControlPanelProps) => {
  // Model fetching state
  const [models, setModels] = useState<string[]>([]);
  const [promptStrats, setPromptStrats] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Add a ref to track button clicks and prevent double execution
  const isRefactoring = useRef(false);

  // Fetch available models from backend
  useEffect(() => {
    const loadModels = async () => {
      setIsLoading(true);
      try {
        const modelNames = await fetchModels(isOnline);
        setModels(modelNames);
        setError(null);
      } catch (error) {
        console.error("Error fetching models:", error);
        setError("Failed to load model list.");
        setModels(["deepseek-1", "llama3.1", "qwen2.5"]); // Fallback models
      } finally {
        setIsLoading(false);
      }
    };

    loadModels();
  }, [isOnline]); // Re-fetch models when isOnline changes

  // Fetch available prompt engineering techniques
  useEffect(() => {
    const loadPromptStrategies = async () => {
      setIsLoading(true);
      try {
        const promptEngTechniques = await fetchPromptStrategies();
        setPromptStrats(promptEngTechniques)
        setError(null)
      } catch (error) {
        console.error("Error fetching models:", error);
        setError("Failed to load prompt strategies...");
        setPromptStrats(["DEFAULT"]); // Fallback prompt
      } finally {
        setIsLoading(false);
      }
    };
      loadPromptStrategies();
  }, []);

  // Create a debounced version of onRefactor to prevent double calls
  const handleRefactorClick = () => {
    if (isRefactoring.current) return;
    
    isRefactoring.current = true;
    
    // Call the provided onRefactor function
    onRefactor();
    
    // Reset the flag after a short delay
    setTimeout(() => {
      isRefactoring.current = false;
    }, 500); // 500ms should be enough to prevent accidental double clicks
  };

  return (
    <div
      className="bg-[#5a6a50]/90 w-80 p-4 text-white overflow-y-auto rounded-r-md shadow-lg"
      style={{ height: "80vh" }}
    >
      <h2 className="text-xl font-medium mb-4 md:mb-6">Refactor Settings</h2>

      {/* File Name Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">File Name</label>
        <input
          type="text"
          placeholder="Enter file name"
          className={`w-full bg-[#4c5944] rounded px-3 py-2 text-white placeholder:text-gray-300/50 focus:outline-none focus:ring-1 focus:ring-[#8ea382] ${
            filesUploaded ? "opacity-50 cursor-not-allowed" : ""
          }`}
          value={fileName}
          onChange={(e) => setFileName(e.target.value)}
          disabled={filesUploaded}
        />
        {language && (
          <p className="text-xs text-gray-300/70 mt-1">
            Will be saved with {getFileExtension(language)} extension
          </p>
        )}
        {filesUploaded && (
          <p className="text-xs text-gray-300/70 mt-1">
            Name locked when files are uploaded
          </p>
        )}
      </div>

      {/* Language Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Language</label>
        <div className="grid grid-cols-2 gap-2">
          {LANGUAGES.map((lang) => (
            <div key={lang} className="flex items-center">
              <input
                type="radio"
                id={`lang-${lang}`}
                name="language"
                className="mr-2 accent-[#8ea382]"
                checked={language === lang}
                onChange={() => setLanguage(lang)}
                disabled={filesUploaded}
              />
              <label
                htmlFor={`lang-${lang}`}
                className={`text-sm cursor-pointer ${
                  filesUploaded ? "opacity-50 cursor-not-allowed" : ""
                }`}
              >
                {lang.charAt(0).toUpperCase() + lang.slice(1)}
              </label>
            </div>
          ))}
        </div>
        {filesUploaded && (
          <p className="text-xs text-gray-300/70 mt-1">
            Language is determined by uploaded files
          </p>
        )}
        {!language && !filesUploaded && (
          <p className="text-xs text-gray-300/70 mt-1">
            Please select a language to continue
          </p>
        )}
      </div>

      {/* Model Type Selection (Online/Local) */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Model Type</label>
        <div className="flex gap-4">
          <div className="flex items-center">
            <input
              type="radio"
              id="online-models"
              name="model-type"
              className="mr-2 accent-[#8ea382]"
              checked={isOnline}
              onChange={() => setIsOnline(true)}
            />
            <label htmlFor="online-models" className="text-sm cursor-pointer">
              Online
            </label>
          </div>
          <div className="flex items-center">
            <input
              type="radio"
              id="local-models"
              name="model-type"
              className="mr-2 accent-[#8ea382]"
              checked={!isOnline}
              onChange={() => setIsOnline(false)}
            />
            <label htmlFor="local-models" className="text-sm cursor-pointer">
              Local
            </label>
          </div>
        </div>
        <p className="text-xs text-gray-300/70 mt-1">
          {isOnline ? "Using online models via API" : "Using locally installed models"}
        </p>
      </div>

      {/* Model Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Model</label>
        {isLoading ? (
          <div className="text-sm py-2">Loading models...</div>
        ) : error ? (
          <div className="text-sm text-red-300 py-2">{error}</div>
        ) : (
          <ModelDropdown
            selectedModel={model}
            setSelectedModel={setModel}
            models={models}
          />
        )}
      </div>

      {/* Temperature Slider */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-1">
          <label className="block text-sm font-medium">Temperature</label>
          <span className="text-sm font-mono bg-[#4c5944] px-2 py-0.5 rounded">
            {temperature}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs">Precise</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={temperature}
            onChange={(e) => setTemperature(parseFloat(e.target.value))}
            className="w-full accent-[#8ea382] h-2 bg-[#4c5944] rounded cursor-pointer"
          />
          <span className="text-xs">Creative</span>
        </div>
        <p className="text-xs text-gray-300/70 mt-1">
          Lower values produce more deterministic output, higher values more
          creative
        </p>
      </div>

      <div className="mb-6">
        <label className="block text-sm font-medium mb-1">Prompt Engineering Strategy</label>
        <div className="space-y-1">
          {promptStrats.map((type) => (
            <div key={type} className="flex items-center">
              <input
                type="radio"
                id={`prompt-${type}`}
                name="prompt-type"
                className="mr-2 accent-[#8ea382]"
                checked={promptStrategy === type}
                onChange={() => setPromptStrategy(type)}
              />
              <label
                htmlFor={`prompt-${type}`}
                className="text-sm cursor-pointer"
              >
                {getPromptTypeLabel(type)}
              </label>
            </div>
          ))}
        </div>
      </div>

      {/* Refactor Button */}
      <button
        onClick={handleRefactorClick} // Using the debounced handler
        className={`w-full py-3 rounded-md transition-colors font-medium ${
          language && model
            ? "bg-[#3d4937] hover:bg-[#4c5944]"
            : "bg-[#3d4937]/50 cursor-not-allowed"
        }`}
        disabled={!language || !model || isRefactoring.current}
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