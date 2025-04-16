"use client";

import { useState, useEffect } from "react";
import EditorWorkspace from "./components/EditorWorkspace";
import ControlPanel from "./components/ControlPanel";
import LoadingScreen, { RefactoredData } from "./components/LoadingScreen";
import ResultsPage from "./components/ResultsPage";
import WelcomeScreen from "./components/WelcomeScreen";

export type FileData = {
  id: string;
  name: string;
  language: string | null;
  content: string;
};

export default function Home() {
  // Application state
  const [workspace, setWorkspace] = useState<{
    files: FileData[];
    activeFileId: string | null;
    editorVisible: boolean;
    filesUploaded: boolean;
  }>({
    files: [],
    activeFileId: null,
    editorVisible: false,
    filesUploaded: false,
  });

  // Control panel state
  const [controlPanel, setControlPanel] = useState({
    visible: false,
    fileName: "New File",
    language: null as string | null,
    model: null as string | null,
    promptType: "basic" as string,
    temperature: 0.7,
  });

  // Process state
  const [processState, setProcessState] = useState<{
    isLoading: boolean;
    error: string | null;
    refactoredData: RefactoredData | null;
  }>({
    isLoading: false,
    error: null,
    refactoredData: null,
  });

  // Function to get appropriate file extension based on language
  const getFileExtension = (lang: string | null): string => {
    if (!lang) return "";
    const extensions: Record<string, string> = {
      java: ".java",
      kotlin: ".kt",
      "c#": ".cs",
      python: ".py",
      javascript: ".js",
      typescript: ".ts",
      html: ".html",
      css: ".css",
      plaintext: ".txt",
    };
    return extensions[lang] || "";
  };

  // Function to remove file extension
  const removeFileExtension = (fileName: string): string => {
    const lastDotIndex = fileName.lastIndexOf(".");
    if (lastDotIndex === -1) return fileName;
    return fileName.substring(0, lastDotIndex);
  };

  // Helper to get the active file
  const getActiveFile = (): FileData | null => {
    if (!workspace.activeFileId || workspace.files.length === 0) return null;
    return (
      workspace.files.find((file) => file.id === workspace.activeFileId) || null
    );
  };

  // Get the current code from the active file
  const getCurrentCode = (): string => {
    const activeFile = getActiveFile();
    return activeFile ? activeFile.content : "";
  };

  // Handle file upload
  const handleFileUpload = async (files: FileList) => {
    if (files.length > 0) {
      const fileArray = Array.from(files);

      const fileDataArray: FileData[] = await Promise.all(
        fileArray.map(async (file) => {
          const content = await file.text();
          const extension = file.name.split(".").pop()?.toLowerCase();

          const languageMap: { [key: string]: string } = {
            py: "python",
            java: "java",
            cpp: "cpp",
            cs: "c#",
            js: "javascript",
            ts: "typescript",
            tsx: "typescript",
            jsx: "javascript",
            kt: "kotlin",
            html: "html",
            css: "css",
          };

          const language = languageMap[extension || ""] || "plaintext";

          return {
            id: crypto.randomUUID(),
            name: file.name,
            content,
            language,
          };
        })
      );

      // Update workspace state with filesUploaded set to true
      setWorkspace({
        files: fileDataArray,
        activeFileId: fileDataArray[0]?.id || null,
        editorVisible: true,
        filesUploaded: true,
      });

      // Update control panel with the active file's language
      setControlPanel((prev) => ({
        ...prev,
        fileName: fileDataArray[0]?.name || "New File",
        language: fileDataArray[0]?.language || null,
      }));
    }
  };

  // Handle creating a new file
  const handleCreateNewFile = () => {
    const newFile: FileData = {
      id: crypto.randomUUID(),
      name: "New File",
      language: null, // Start with no language selected
      content: "",
    };

    setWorkspace({
      files: [newFile],
      activeFileId: newFile.id,
      editorVisible: true,
      filesUploaded: false,
    });

    setControlPanel((prev) => ({
      ...prev,
      fileName: newFile.name,
      language: null, // Start with no language selected
    }));
  };

  // Handle file content change
  const handleCodeChange = (content: string) => {
    if (!workspace.activeFileId) return;

    setWorkspace((prev) => ({
      ...prev,
      files: prev.files.map((file) =>
        file.id === prev.activeFileId ? { ...file, content } : file
      ),
    }));
  };

  // Handle file tab change
  const handleFileChange = (fileId: string) => {
    const file = workspace.files.find((f) => f.id === fileId);
    if (!file) return;

    setWorkspace((prev) => ({
      ...prev,
      activeFileId: fileId,
    }));

    setControlPanel((prev) => ({
      ...prev,
      fileName: file.name,
      language: file.language,
    }));
  };

  // Toggle control panel visibility
  const toggleControlPanel = () => {
    setControlPanel((prev) => ({
      ...prev,
      visible: !prev.visible,
    }));
  };

  // Handle file name change, preserving the extension
  const handleFileNameChange = (newFileName: string) => {
    if (workspace.filesUploaded) return;

    const activeFile = getActiveFile();
    if (!activeFile) return;

    // Get the base name without extension
    const currentBaseName = removeFileExtension(activeFile.name);

    // If the new name already has an extension, ignore it
    const newBaseName = removeFileExtension(newFileName);

    // Create the new full name with the original extension
    const extension = getFileExtension(activeFile.language);
    const fullNewName = newBaseName + extension;

    // Update the control panel and file
    setControlPanel((prev) => ({
      ...prev,
      fileName: fullNewName,
    }));

    setWorkspace((prev) => ({
      ...prev,
      files: prev.files.map((file) =>
        file.id === prev.activeFileId ? { ...file, name: fullNewName } : file
      ),
    }));
  };

  // Handle language change
  const handleLanguageChange = (newLanguage: string | null) => {
    if (workspace.filesUploaded) return;

    const activeFile = getActiveFile();
    if (!activeFile) return;

    // Get the base name without current extension
    const baseName = removeFileExtension(activeFile.name);

    // Add the new extension based on the language
    const newExtension = getFileExtension(newLanguage);
    const newFileName = baseName + newExtension;

    // Update control panel
    setControlPanel((prev) => ({
      ...prev,
      language: newLanguage,
      fileName: newFileName,
    }));

    // Update workspace
    setWorkspace((prev) => ({
      ...prev,
      files: prev.files.map((file) =>
        file.id === prev.activeFileId
          ? { ...file, language: newLanguage, name: newFileName }
          : file
      ),
    }));
  };

  // Handle refactor button click
  const handleRefactor = () => {
    const currentCode = getCurrentCode();

    if (!currentCode.trim()) {
      alert("Please enter some code to refactor");
      return;
    }

    if (!controlPanel.language) {
      alert("Please select a language");
      return;
    }

    if (!controlPanel.model) {
      alert("Please select a model");
      return;
    }

    // Show loading screen
    setProcessState({
      isLoading: true,
      error: null,
      refactoredData: null,
    });
  };

  // Handle loading complete
  const handleLoadingComplete = (data: RefactoredData) => {
    setProcessState({
      isLoading: false,
      error: null,
      refactoredData: data,
    });
  };

  // Handle loading error
  const handleLoadingError = (errorMessage: string) => {
    setProcessState({
      isLoading: false,
      error: errorMessage,
      refactoredData: null,
    });
  };

  // Handle going back to editor
  const handleBackToEditor = () => {
    setProcessState({
      isLoading: false,
      error: null,
      refactoredData: null,
    });
  };

  // Render error screen if there's an error
  if (processState.error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#505a46] text-white">
        <div className="text-2xl mb-4 text-red-300">Error</div>
        <div className="text-lg mb-8">{processState.error}</div>
        <button
          onClick={handleBackToEditor}
          className="bg-[#3F4637] hover:bg-[#68765A] text-white px-4 py-2 rounded-md transition-colors"
        >
          Back to Editor
        </button>
      </div>
    );
  }

  // Render results page if refactored data exists
  if (processState.refactoredData) {
    return (
      <ResultsPage
        refactoredData={processState.refactoredData}
        onClose={handleBackToEditor}
      />
    );
  }

  return (
    <div className="flex flex-col min-h-screen font-[family-name:var(--font-geist-sans)] overflow-x-hidden">
      {/* Loading Screen */}
      {processState.isLoading && (
        <LoadingScreen
          isLoading={processState.isLoading}
          onLoadingComplete={handleLoadingComplete}
          onError={handleLoadingError}
          originalCode={getCurrentCode()}
          originalFileName={controlPanel.fileName}
          modelSelected={controlPanel.model || ""}
          promptType={controlPanel.promptType}
          language={controlPanel.language}
          temperature={controlPanel.temperature}
        />
      )}

      {/* Header with logo */}
      <div className="py-6 px-10">
        <img
          src="/icons/refactoraptor-logo.svg"
          alt="Refactoraptor Logo"
          className="w-50 h-auto cursor-pointer transition-transform hover:scale-110 active:scale-95 rounded-2xl px-2 py-2"
          onClick={() => (window.location.href = "/")}
        />
      </div>

      {/* Main Content */}
      <div className="flex-grow flex justify-center items-center px-4">
        <main className="flex flex-col items-center w-full max-w-7xl">
          {!workspace.editorVisible ? (
            <WelcomeScreen
              onUploadFiles={(event) => {
                if (event.target.files) {
                  handleFileUpload(event.target.files);
                }
              }}
              onCreateNew={handleCreateNewFile}
            />
          ) : (
            <div className="flex w-full">
              {/* Editor Workspace */}
              <EditorWorkspace
                files={workspace.files}
                activeFileId={workspace.activeFileId}
                onFileChange={handleFileChange}
                onCodeChange={handleCodeChange}
                toggleControlPanel={toggleControlPanel}
              />

              {/* Control Panel */}
              {controlPanel.visible && (
                <ControlPanel
                  fileName={removeFileExtension(controlPanel.fileName)}
                  setFileName={handleFileNameChange}
                  language={controlPanel.language}
                  setLanguage={handleLanguageChange}
                  model={controlPanel.model}
                  setModel={(model) =>
                    setControlPanel((prev) => ({ ...prev, model }))
                  }
                  promptType={controlPanel.promptType}
                  setPromptType={(promptType) =>
                    setControlPanel((prev) => ({ ...prev, promptType }))
                  }
                  temperature={controlPanel.temperature}
                  setTemperature={(temperature) =>
                    setControlPanel((prev) => ({ ...prev, temperature }))
                  }
                  onRefactor={handleRefactor}
                  filesUploaded={workspace.filesUploaded}
                />
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
