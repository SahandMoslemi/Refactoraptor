"use client";

import { useState } from "react";
import CodeEditor from "./components/CodeEditor";
import ControlPanel from "./components/ControlPanel";
import LoadingScreen, { RefactoredData } from "./components/LoadingScreen";
import ResultsPage from "./components/ResultsPage";
import CodeEditorTabs from "./components/CodeEditorTabs";

type FileProp = {
  name: string;
  language: string;
  content: string;
};

export default function Home() {
  // File state
  const [files, setFiles] = useState<FileProp[]>([]);
  const [activeFile, setActiveFile] = useState<FileProp | null>(null);
  const [showIcons, setShowIcons] = useState(true);

  // Main app state
  const [currentCode, setCurrentCode] = useState("");
  const [fileName, setFileName] = useState("New File");
  const [language, setLanguage] = useState<string | null>(null);
  const [model, setModel] = useState<string | null>(null);
  const [promptType, setPromptType] = useState<string>("basic");

  // Process state
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refactoredData, setRefactoredData] = useState<RefactoredData | null>(null);

  // Handle file upload
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = event.target.files;
    if (selectedFiles) {
      const fileArray = Array.from(selectedFiles);

      const filePropArray: FileProp[] = await Promise.all(
        fileArray.map(async (file) => {
          const content = await file.text();
          const extension = file.name.split(".").pop()?.toLowerCase();

          const languageMap: { [key: string]: string } = {
            py: "python",
            java: "java",
            cpp: "cpp",
            cs: "csharp",
            kt: "kotlin"
          };

          const language = languageMap[extension || ""] || "plaintext";

          return {
            name: file.name,
            content,
            language,
          };
        })
      );

      setFiles(filePropArray);
      
      // Update active file and editor content
      const firstFile = filePropArray[0];
      setActiveFile(firstFile);
      setCurrentCode(firstFile.content);
      setFileName(firstFile.name);
      setLanguage(firstFile.language);
      
      setShowIcons(false); // Hide icons after uploading
    }
  };

  const handleWriteCode = () => {
    setShowIcons(false); // Hide icons on click
    setCurrentCode("");
    setFileName("New File");
    setLanguage("java");
  };

  // Handle refactor button click
  const handleRefactor = () => {
    if (!currentCode.trim()) {
      alert("Please enter some code to refactor");
      return;
    }

    if (!language) {
      alert("Please select a language");
      return;
    }

    if (!model) {
      alert("Please select a model");
      return;
    }

    // Show loading screen
    setIsLoading(true);
    setError(null);
  };

  // Handle loading complete
  const handleLoadingComplete = (data: RefactoredData) => {
    setIsLoading(false);
    setRefactoredData(data);
  };

  // Handle loading error
  const handleLoadingError = (errorMessage: string) => {
    setIsLoading(false);
    setError(errorMessage);
  };

  // Handle going back to editor
  const handleBackToEditor = () => {
    setRefactoredData(null);
    setError(null);
  };

  // Handle file tab change
  const handleTabChange = (file: FileProp) => {
    setActiveFile(file);
    setCurrentCode(file.content);
    setFileName(file.name);
    setLanguage(file.language);
  };

  // If there's an error, show error message
  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#606b50] text-white">
        <div className="text-2xl mb-4 text-red-300">Error</div>
        <div className="text-lg mb-8">{error}</div>
        <button
          onClick={() => setError(null)}
          className="bg-[#4c5944] hover:bg-[#3d4937] text-white px-4 py-2 rounded-md transition-colors"
        >
          Back to Editor
        </button>
      </div>
    );
  }

  // If refactored data exists, show results page
  if (refactoredData) {
    return (
      <ResultsPage
        refactoredData={refactoredData}
        onClose={handleBackToEditor}
      />
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-[#606b50] font-[family-name:var(--font-geist-sans)] overflow-x-hidden">
      {/* Loading Screen */}
      {isLoading && (
        <LoadingScreen
          isLoading={isLoading}
          onLoadingComplete={handleLoadingComplete}
          onError={handleLoadingError}
          originalCode={currentCode}
          originalFileName={fileName}
          modelSelected={model || ""}
          promptType={promptType}
        />
      )}

      {/* Title at the Top */}
      <div className="py-6 px-10">
        <img
          src="/icons/refactoraptor-logo.svg"
          alt="Refactoraptor Logo"
          className="w-50 h-auto cursor-pointer transition-transform hover:scale-110 active:scale-95 rounded-2xl px-2 py-2"
          onClick={() => window.location.href = "/"}
        />
      </div>

      {/* Main Content Centered Vertically */}
      <div className="flex-grow flex justify-center items-center">
        <main className="flex flex-col items-center gap-10 w-full max-w-7xl">
          {/* Icons Section */}
          {showIcons && (
            <div className="flex items-center gap-64">
              {/* Upload File Icon */}
              <div className="flex flex-col items-center cursor-pointer transition-transform hover:scale-110 active:scale-95">
                <img
                  src="/icons/upload-icon.svg"
                  alt="Upload Files"
                  className="w-16 h-16 filter invert"
                  onClick={() => document.getElementById("file-input")?.click()}
                />
                <label className="text-white mt-2">Upload Files</label>
                <input
                  id="file-input"
                  type="file"
                  multiple
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </div>

              {/* Divider */}
              <div className="h-125 border-l-2 border-white" />

              {/* Write Code Icon */}
              <div
                className="flex flex-col items-center cursor-pointer transition-transform hover:scale-110 active:scale-95"
                onClick={handleWriteCode}
              >
                <img
                  src="/icons/write-icon.svg"
                  alt="Write Code"
                  className="w-16 h-16 filter invert"
                />
                <label className="text-white mt-2">Write Code</label>
              </div>
            </div>
          )}

          {/* Editor and Control Panel */}
          {!showIcons && (
            <div className="flex-1 flex flex-col md:flex-row rounded-md overflow-hidden w-full">
              {/* Left side - Code Editor */}
              <div
                style={{ flex: '1 1 auto', minWidth: '0' }}
                className="bg-[#1e1e1e] rounded-t-md md:rounded-l-md md:rounded-tr-none min-h-[60vh] md:min-h-0"
              >
                {files.length > 0 ? (
                  <CodeEditorTabs 
                    files={files} 
                    activeFile={activeFile} 
                    onTabChange={handleTabChange}
                  />
                ) : (
                  <CodeEditor
                    value={currentCode}
                    onChange={(value) => setCurrentCode(value || "")}
                    language={language || "java"}
                  />
                )}
              </div>

              {/* Right side - Control Panel */}
              <div
                style={{ flex: '0 0 320px' }}
                className="bg-[#5a6a50] rounded-b-md md:rounded-r-md md:rounded-bl-none"
              >
                <ControlPanel
                  fileName={fileName}
                  setFileName={setFileName}
                  language={language}
                  setLanguage={setLanguage}
                  model={model}
                  setModel={setModel}
                  promptType={promptType}
                  setPromptType={setPromptType}
                  onRefactor={handleRefactor}
                />
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}