"use client";

import React, { useState, useRef, useEffect } from "react";
import { RefactoredData } from "./LoadingScreen";
import EditorWorkspace from "./EditorWorkspace";
import { FileData } from "../page";

// Add custom scrollbar styles 
const scrollbarStyles = `
  .custom-scrollbar::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  .custom-scrollbar::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: #748569;
    border-radius: 4px;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #5c6a54;
  }
`;

interface ResultsPageProps {
  refactoredData: RefactoredData;
  onClose: () => void;
}

const ResultsPage: React.FC<ResultsPageProps> = ({
  refactoredData,
  onClose,
}) => {
  const [showExplanation, setShowExplanation] = useState(false);
  const explanationRef = useRef<HTMLDivElement>(null);
  const monacoRef = useRef<any>(null);

  // State for file management
  const [originalFiles, setOriginalFiles] = useState<FileData[]>([]);
  const [refactoredFiles, setRefactoredFiles] = useState<FileData[]>([]);
  const [activeOriginalFileId, setActiveOriginalFileId] = useState<
    string | null
  >(null);
  const [activeRefactoredFileId, setActiveRefactoredFileId] = useState<
    string | null
  >(null);

  // Extract data from refactoredData
  const {
    originalCode,
    refactoredCode,
    codeChanges,
    executionTime,
    modelUsed,
    originalFileName,
    language,
    explanation,
    violation_type
  } = refactoredData;

  const languageExtensions: { [key: string]: string } = {
    java: "java",
    python: "py",
    kotlin: "kt",
    "c#": "cs",
    csharp: "cs",
    javascript: "js",
    typescript: "ts",
  };

  // Generate refactored file name based on the selected language
  const getRefactoredFileName = () => {
    // Try to get the extension from the original file name first
    if (originalFileName.includes(".")) {
      return `Refactored.${originalFileName.split(".").pop()}`;
    }

    // If no extension in the file name, use the selected language
    if (language && languageExtensions[language.toLowerCase()]) {
      return `Refactored.${languageExtensions[language.toLowerCase()]}`;
    }

    // Default extension if nothing else works
    return "Refactored.txt";
  };

  const refactoredFileName = getRefactoredFileName();

  // Initialize files on component mount
  useEffect(() => {
    // Create file data objects for original and refactored code
    const originalFileData: FileData = {
      id: "original-1",
      name: originalFileName,
      content: originalCode,
      language: language || "java",
    };

    const refactoredFileData: FileData = {
      id: "refactored-1",
      name: refactoredFileName,
      content: refactoredCode,
      language: language || "java",
    };

    setOriginalFiles([originalFileData]);
    setRefactoredFiles([refactoredFileData]);
    setActiveOriginalFileId("original-1");
    setActiveRefactoredFileId("refactored-1");
  }, [
    originalCode,
    refactoredCode,
    originalFileName,
    refactoredFileName,
    language,
  ]);

  useEffect(() => {
    if (showExplanation && explanationRef.current) {
      // Reset scroll position when explanation is shown
      explanationRef.current.scrollTop = 0;
    }
  }, [showExplanation]);

  // Handle multiple violation types
  const getViolationTypeTags = () => {
    // Split violation types if they contain commas
    const violationTypes = violation_type ? violation_type.split(',').map(type => type.trim()) : [];
    
    const violationMap: { [key: string]: { bg: string, text: string } } = {
      "Performance": { bg: "bg-amber-100", text: "text-amber-800" },
      "Security": { bg: "bg-red-100", text: "text-red-800" },
      "Maintainability": { bg: "bg-blue-100", text: "text-blue-800" },
      "Code Smell": { bg: "bg-purple-100", text: "text-purple-800" },
      "Bug": { bg: "bg-orange-100", text: "text-orange-800" },
      "Design": { bg: "bg-indigo-100", text: "text-indigo-800" },
      "Complexity": { bg: "bg-emerald-100", text: "text-emerald-800" },
    };

    return violationTypes.map(type => {
      // Default styling if violation type is not in our map
      const style = violationMap[type] || { bg: "bg-gray-100", text: "text-gray-800" };
      return { type, style };
    });
  };

  const handleSave = () => {
    // Find the active refactored file
    const activeFile = refactoredFiles.find(
      (file) => file.id === activeRefactoredFileId
    );
    if (!activeFile) return;

    // Create a blob and trigger download
    const blob = new Blob([activeFile.content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = activeFile.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const toggleExplanation = () => {
    setShowExplanation(!showExplanation);
  };

  // Handlers for EditorWorkspace
  const handleOriginalFileChange = (fileId: string) => {
    setActiveOriginalFileId(fileId);
  };

  const handleRefactoredFileChange = (fileId: string) => {
    setActiveRefactoredFileId(fileId);
  };

  const handleOriginalCodeChange = (content: string) => {
    // Update the content of the active original file
    if (activeOriginalFileId) {
      setOriginalFiles((prev) =>
        prev.map((file) =>
          file.id === activeOriginalFileId ? { ...file, content } : file
        )
      );
    }
  };

  const handleRefactoredCodeChange = (content: string) => {
    // Update the content of the active refactored file
    if (activeRefactoredFileId) {
      setRefactoredFiles((prev) =>
        prev.map((file) =>
          file.id === activeRefactoredFileId ? { ...file, content } : file
        )
      );
    }
  };

  // Define action buttons for the refactored editor
  const refactoredEditorButtons = [
    {
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
      label: "Show explanation",
      onClick: toggleExplanation,
    },
    {
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
          />
        </svg>
      ),
      label: "Save refactored code",
      onClick: handleSave,
    },
  ];

  return (
    <div className="h-screen flex flex-col bg-[#505a46] font-[family-name:var(--font-geist-sans)] overflow-hidden">
      {/* Inject custom scrollbar styles */}
      <style>{scrollbarStyles}</style>
      
      {/* Header */}
      <header className="p-4 flex justify-between items-center">
        <div className="py-2 px-6">
          <img
            src="/icons/refactoraptor-logo.svg"
            alt="Refactoraptor Logo"
            className="w-50 h-auto cursor-pointer transition-transform hover:scale-110 active:scale-95 rounded-2xl px-2 py-2"
            onClick={() => (window.location.href = "/")}
          />
        </div>
        <div className="flex items-center">
          <div className="mr-4">
            {executionTime && modelUsed && (
              <div className="text-white/70 text-sm text-right">
                Refactored in {executionTime} using {modelUsed}
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="bg-[#748569] hover:bg-[#3d4937] text-white px-4 py-2 rounded-md transition-colors"
          >
            Back to Editor
          </button>
        </div>
      </header>

      {/* Main Content - Code Comparison */}
      <main className="flex-1 flex flex-col px-4 pb-4">
        {/* Side by side editors with responsive behavior */}
        <div className="flex-1 flex flex-col md:flex-row gap-4">
          {/* Original Code */}
          <div className="w-full md:w-1/2 relative">
            <EditorWorkspace
              files={originalFiles}
              activeFileId={activeOriginalFileId}
              onFileChange={handleOriginalFileChange}
              onCodeChange={handleOriginalCodeChange}
              mode="results"
              showButtons={false} // No buttons for original code editor
            />
          </div>

          {/* Refactored Code */}
          <div className="w-full md:w-1/2 mt-4 md:mt-0 relative">
            <EditorWorkspace
              files={refactoredFiles}
              activeFileId={activeRefactoredFileId}
              onFileChange={handleRefactoredFileChange}
              onCodeChange={handleRefactoredCodeChange}
              mode="results"
              actionButtons={refactoredEditorButtons}
            />

            {/* Explanation overlay when showing - matching editor height exactly */}
            {showExplanation && (
              <div className="absolute top-[37px] left-0 right-0 bottom-0 bg-black/80 text-white overflow-hidden z-30 flex flex-col">
                <div className="flex justify-between items-center border-b border-gray-700 p-4">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="text-lg font-medium mr-2">Refactoring Explanation</h3>
                    {getViolationTypeTags().map((violation, index) => (
                      <span 
                        key={index} 
                        className={`px-3 py-1 rounded-full text-sm font-medium ${violation.style.bg} ${violation.style.text} my-1`}
                      >
                        {violation.type}
                      </span>
                    ))}
                  </div>
                  <button
                    onClick={toggleExplanation}
                    className="text-gray-400 hover:text-white"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
                
                <div 
                  ref={explanationRef}
                  className="flex-grow p-4 overflow-y-auto custom-scrollbar"
                >
                  <div className="prose prose-invert max-w-none">
                    <p className="mb-4 text-gray-200">
                      {explanation}
                    </p>
                    
                    {/* {codeChanges && codeChanges.length > 0 && (
                      <div className="mt-6">
                        <h4 className="text-md font-medium mb-3 text-gray-300">Changes Made:</h4>
                        <ul className="space-y-3">
                          {codeChanges.map((change, index) => (
                            <li key={index} className="p-2 bg-gray-800/50 rounded">
                              <span className="text-yellow-300 font-medium">
                                Line {change.lineNumber}:
                              </span>{" "}
                              {change.explanation}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )} */}
                  </div>
                </div>
                
                {/* Custom scroll bar slider */}
                {/* <div className="px-4 pb-3 pt-1 border-t border-gray-700">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={scrollPosition}
                    onChange={handleScroll}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-[#748569]"
                  />
                </div> */}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default ResultsPage;