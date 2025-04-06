"use client";

import { useState } from "react";
import CodeEditor from "./components/CodeEditor";
import ControlPanel from "./components/ControlPanel";
import LoadingScreen, { RefactoredData } from "./components/LoadingScreen";
import ResultsPage from "./components/ResultsPage";

export default function Home() {
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
        <div className="min-h-screen flex flex-col bg-[#606b50] font-[family-name:var(--font-geist-sans)] overflow-x-hidden">
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

            {/* Header */}
            <header className="p-4">
                <h1 className="text-2xl text-white font-medium">Refactoraptor</h1>
            </header>

            {/* Main Content */}
            <main className="flex-1 flex flex-col p-4 overflow-hidden">
                <div className="flex-1 flex flex-col md:flex-row rounded-md overflow-hidden">
                    {/* Left side - Code Editor */}
                    <div
                        style={{ flex: '1 1 auto', minWidth: '0' }}
                        className="bg-[#1e1e1e] rounded-t-md md:rounded-l-md md:rounded-tr-none min-h-[60vh] md:min-h-0"
                    >
                        <CodeEditor
                            value={currentCode}
                            onChange={(value) => setCurrentCode(value || "")}
                            language={language || "java"}
                        />
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
            </main>

        </div>
    );
}