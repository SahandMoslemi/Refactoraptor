"use client";

import React, { useEffect, useRef } from "react";
import { refactorCode, RefactoredData } from "../api/refactorService";
import { useLoadingDots, useProcessStatus } from "../utils/loadingUtils";

interface LoadingScreenProps {
  isLoading: boolean;
  onLoadingComplete: (data: RefactoredData) => void;
  onError: (error: string) => void;
  originalCode: string;
  originalFileName: string;
  modelSelected: string;
  promptType: string;
  language: string;
  temperature: number;
  isOnline: boolean
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
  isOnline,
}) => {
  // Use custom hooks for loading state management
  const dots = useLoadingDots(500);
  const [status, setStatus] = useProcessStatus("Initializing...");
  
  // Use a ref to track if the refactoring API call is in progress
  const refactoringInProgress = useRef(false);
  // Use a ref to track if this effect has already run
  const effectHasRun = useRef(false);

  useEffect(() => {
    // Skip if not loading or if either flag is set
    if (!isLoading || refactoringInProgress.current || effectHasRun.current) return;

    // Log request parameters
    console.log("Sending request to backend with:", {
      originalCode,
      fileName: originalFileName,
      model: modelSelected,
      promptType,
      language,
      temperature,
      isOnline,
    });

    // Set both flags to prevent duplicate calls
    refactoringInProgress.current = true;
    effectHasRun.current = true;
    
    // Perform refactoring
    const performRefactoring = async () => {
      try {
        setStatus("Refactoring");

        const refactoredData = await refactorCode(
          originalCode,
          modelSelected,
          promptType.toUpperCase(),
          originalFileName,
          language,
          temperature,
          isOnline,
        );

        setStatus("Refactoring complete!");
        
        // Small delay to show completion status
        setTimeout(() => {
          onLoadingComplete(refactoredData);
          // Reset flags after completion
          refactoringInProgress.current = false;
        }, 300);
      } catch (err) {
        console.error("Error refactoring code:", err);
        onError(
          err instanceof Error
            ? err.message
            : "Failed to refactor code. Please try again."
        );
        // Reset flags after error
        refactoringInProgress.current = false;
      }
    };

    performRefactoring();
    
    // Cleanup function to handle component unmount during operation
    return () => {
      // If the component unmounts during operation, we should reset the flags
      if (refactoringInProgress.current) {
        console.log("Component unmounted during refactoring operation");
        refactoringInProgress.current = false;
      }
    };
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