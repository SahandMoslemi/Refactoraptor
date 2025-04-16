"use client";

import React, { useEffect } from "react";
import { RefactorService, RefactoredData } from "../api/refactorService";
import { useLoadingDots, useProcessStatus } from "../utils/loadingUtils";

interface LoadingScreenProps {
  isLoading: boolean;
  onLoadingComplete: (data: RefactoredData) => void;
  onError: (error: string) => void;
  originalCode: string;
  originalFileName: string;
  modelSelected: string;
  promptType: string;
  language: string | null;
  temperature: number;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({
  isLoading,
  onLoadingComplete,
  onError,
  originalCode,
  originalFileName,
  modelSelected,
  promptType,
  language,
  temperature,
}) => {
  const dots = useLoadingDots(500);
  const [status, setStatus] = useProcessStatus("Initializing...");
  const refactorService = new RefactorService();

  useEffect(() => {
    if (!isLoading) return;

    // Log request parameters
    console.log("Sending request to backend with:", {
      originalCode,
      fileName: originalFileName,
      model: modelSelected,
      promptType,
      language,
      temperature,
    });

    // Perform refactoring
    const performRefactoring = async () => {
      try {
        setStatus("Refactoring");

        const refactoredData = await refactorService.refactorCode(
          originalCode,
          modelSelected,
          promptType,
          originalFileName,
          language,
          temperature
        );

        setStatus("Refactoring complete!");

        // Small delay to show completion status
        setTimeout(() => {
          onLoadingComplete(refactoredData);
        }, 1000);
      } catch (err) {
        console.error("Error refactoring code:", err);
        onError(
          err instanceof Error
            ? err.message
            : "Failed to refactor code. Please try again."
        );
      }
    };

    performRefactoring();
  }, [
    isLoading,
    originalCode,
    originalFileName,
    modelSelected,
    promptType,
    language,
    temperature,
    onLoadingComplete,
    onError,
    setStatus,
    refactorService,
  ]);

  // Don't render if not loading
  if (!isLoading) return null;

  return (
    <div className="fixed inset-0 flex flex-col items-center justify-center bg-[#505a46] bg-opacity-95 z-50">
      {/* Loading animation */}
      <div className="w-16 h-16 mb-6">
        <img
          src="/load.gif"
          alt="Loading Animation"
          className="w-full h-full object-contain"
        />
      </div>

      {/* Status display */}
      <div className="mt-4 text-white text-lg font-medium">
        {status}
        {dots}
      </div>

      {/* Model and prompt info */}
      <div className="mt-2 text-white/70 text-sm">
        Using {modelSelected} model with {promptType} prompt
      </div>
    </div>
  );
};

export default LoadingScreen;
