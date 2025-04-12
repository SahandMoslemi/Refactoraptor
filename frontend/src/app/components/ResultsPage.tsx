// ResultsPage.tsx
"use client";

import React, { useState, useRef, useEffect } from "react";
import { Editor } from "@monaco-editor/react";
import { RefactoredData } from "./LoadingScreen";

interface ResultsPageProps {
  refactoredData: RefactoredData;
  onClose: () => void;
}

const ResultsPage: React.FC<ResultsPageProps> = ({
  refactoredData,
  onClose,
}) => {
  const [showExplanation, setShowExplanation] = useState(false);
  const originalEditorRef = useRef<any>(null);
  const refactoredEditorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);

  // Extract data from refactoredData
  const {
    originalCode,
    refactoredCode,
    codeChanges,
    executionTime,
    modelUsed,
    originalFileName,
    language,
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

  // Function to highlight specific lines in the code
  const highlightLines = (
    editorRef: React.MutableRefObject<any>,
    lineNumbers: number[]
  ) => {
    if (!editorRef.current || !monacoRef.current) return;

    const editor = editorRef.current;
    const monaco = monacoRef.current;

    const decorations = lineNumbers.map((lineNumber) => ({
      range: new monaco.Range(lineNumber, 1, lineNumber, 1),
      options: {
        isWholeLine: true,
        className: "highlight-line",
        glyphMarginClassName: "highlight-glyph",
      },
    }));

    editor.deltaDecorations([], decorations);
  };

  const handleSave = () => {
    // Create a blob and trigger download
    const blob = new Blob([refactoredCode], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = refactoredFileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const toggleExplanation = () => {
    setShowExplanation(!showExplanation);
  };

  // Function to handle editor mount
  const handleEditorDidMount = (
    editor: any,
    monaco: any,
    ref: React.MutableRefObject<any>
  ) => {
    ref.current = editor;

    // Store monaco reference
    if (!monacoRef.current) {
      monacoRef.current = monaco;

      // Add custom CSS for highlighting
      const style = document.createElement("style");
      style.textContent = `
                .highlight-line { background-color: rgba(255, 255, 100, 0.2); }
                .highlight-glyph { background-color: rgba(255, 255, 0, 0.5); width: 5px !important; margin-left: 3px; }
                body { overflow: hidden; }
            `;
      document.head.appendChild(style);
    }

    // Enable line numbers and glyph margin for highlighting
    editor.updateOptions({
      glyphMargin: true,
    });

    // If this is the refactored editor, highlight all code changes
    if (ref === refactoredEditorRef && codeChanges) {
      setTimeout(() => {
        highlightLines(
          refactoredEditorRef,
          codeChanges.map((change) => change.lineNumber)
        );
      }, 500);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-[#505a46] font-[family-name:var(--font-geist-sans)] overflow-hidden">
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
            className="bg-[#4c5944] hover:bg-[#3d4937] text-white px-4 py-2 rounded-md transition-colors"
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
            {/* File name header */}
            <div className="bg-[#4d5c44] text-white px-4 py-2 font-medium">
              {originalFileName}
            </div>
            <div style={{ height: "calc(100vh - 160px)" }}>
              <Editor
                height="100%"
                width="100%"
                theme="vs-dark"
                defaultLanguage="java"
                value={originalCode}
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  fontSize: 14,
                  lineNumbers: "on",
                  roundedSelection: false,
                  renderLineHighlight: "line",
                }}
                onMount={(editor, monaco) =>
                  handleEditorDidMount(editor, monaco, originalEditorRef)
                }
              />
            </div>

            {/* Circular button in bottom right */}
            <div className="absolute bottom-4 right-4">
              <button
                className="bg-[#3d4937] text-white w-10 h-10 rounded-full flex items-center justify-center opacity-70"
                aria-label="Code info"
              >
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
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </button>
            </div>
          </div>

          {/* Refactored Code */}
          <div className="w-full md:w-1/2 mt-4 md:mt-0 relative">
            {/* File name header */}
            <div className="bg-[#4d5c44] text-white px-4 py-2 font-medium">
              {refactoredFileName}
            </div>
            <div style={{ height: "calc(100vh - 160px)" }}>
              <Editor
                height="100%"
                width="100%"
                theme="vs-dark"
                defaultLanguage="java"
                value={refactoredCode}
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  fontSize: 14,
                  lineNumbers: "on",
                  roundedSelection: false,
                  renderLineHighlight: "line",
                }}
                onMount={(editor, monaco) =>
                  handleEditorDidMount(editor, monaco, refactoredEditorRef)
                }
              />

              {/* Explanation overlay when showing */}
              {showExplanation && (
                <div className="absolute inset-0 bg-black/80 text-white p-6 overflow-auto">
                  <h3 className="text-xl font-medium mb-4">
                    Refactoring Explanation
                  </h3>

                  <div>
                    <p className="mb-4">
                      The following changes were made to improve the code:
                    </p>
                    <ul className="space-y-3">
                      {codeChanges.map((change, index) => (
                        <li key={index} className="p-2 rounded">
                          <span className="text-yellow-300">
                            Line {change.lineNumber}:
                          </span>{" "}
                          {change.explanation}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="mt-4 flex gap-2">
                    <button
                      onClick={toggleExplanation}
                      className="bg-[#4d5c44] hover:bg-[#5c6b51] px-4 py-2 rounded-md"
                    >
                      Close
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Bottom right buttons */}
            <div className="absolute bottom-4 right-4 flex space-x-2">
              {/* Explanation Button */}
              <button
                onClick={toggleExplanation}
                className="bg-[#3d4937] text-white w-10 h-10 rounded-full flex items-center justify-center opacity-70 hover:opacity-100 transition-opacity"
                aria-label="Show explanation"
              >
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
              </button>

              {/* Save Button */}
              <button
                onClick={handleSave}
                className="bg-[#3d4937] text-white w-10 h-10 rounded-full flex items-center justify-center opacity-70 hover:opacity-100 transition-opacity"
                aria-label="Save refactored code"
              >
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
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ResultsPage;
