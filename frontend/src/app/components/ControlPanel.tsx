"use client";

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
  temperature: number;
  setTemperature: (temp: number) => void;
  onRefactor: () => void;
  filesUploaded?: boolean;
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
  temperature,
  setTemperature,
  onRefactor,
  filesUploaded = false,
}: ControlPanelProps) => {
  // Available options
  const languages: Language[] = ["java", "kotlin", "c#", "python"];
  const promptTypes: PromptType[] = [
    "basic",
    "example-based",
    "solid-principles",
  ];

  // Function to get appropriate file extension based on language
  const getFileExtension = (lang: string | null): string => {
    if (!lang) return "";
    const extensions: Record<string, string> = {
      java: ".java",
      kotlin: ".kt",
      "c#": ".cs",
      python: ".py",
    };
    return extensions[lang] || "";
  };

  return (
    <div
      className="bg-[#5a6a50]/90 w-80 p-4 text-white overflow-y-auto rounded-r-md shadow-lg"
      style={{ height: "66vh" }}
    >
      <h2 className="text-xl font-medium mb-4 md:mb-6">Refactor Settings</h2>

      {/* File Name */}
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
          {languages.map((lang) => (
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

      {/* Model Selection - Using ModelDropdown */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Model</label>
        <ModelDropdown
          selectedModel={model as Model | null}
          setSelectedModel={(selectedModel) => setModel(selectedModel)}
        />
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
              <label
                htmlFor={`prompt-${type}`}
                className="text-sm cursor-pointer"
              >
                {type === "basic"
                  ? "Basic prompt"
                  : type === "example-based"
                  ? "Example-based prompt"
                  : "SOLID principles improvement"}
              </label>
            </div>
          ))}
        </div>
      </div>

      {/* Refactor Button */}
      <button
        onClick={onRefactor}
        className={`w-full py-3 rounded-md transition-colors font-medium ${
          language && model
            ? "bg-[#3d4937] hover:bg-[#4c5944]"
            : "bg-[#3d4937]/50 cursor-not-allowed"
        }`}
        disabled={!language || !model}
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
