"use client";

import React, { useEffect, useState } from "react";
import Image from "next/image";

interface CodeChange {
    lineNumber: number;
    explanation: string;
}

export interface RefactoredData {
    originalCode: string;
    refactoredCode: string;
    codeChanges: CodeChange[];
    executionTime?: string;
    modelUsed?: string;
}

interface LoadingScreenProps {
    isLoading: boolean;
    onLoadingComplete: (data: RefactoredData) => void;
    onError: (error: string) => void;
    originalCode: string;
    originalFileName: string;
    modelSelected: string;
    promptType: string;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({
                                                         isLoading,
                                                         onLoadingComplete,
                                                         onError,
                                                         originalCode,
                                                         originalFileName,
                                                         modelSelected,
                                                         promptType
                                                     }) => {
    const [dots, setDots] = useState("");

    useEffect(() => {
        if (!isLoading) return;

        console.log("Backend integration will be added here");
        console.log("Sending request to backend with:", {
            originalCode,
            fileName: originalFileName,
            model: modelSelected,
            promptType
        });

        // Animation for the loading dots
        const dotsInterval = setInterval(() => {
            setDots((prev) => {
                if (prev.length >= 3) {
                    return "";
                }
                return prev + ".";
            });
        }, 500);

        // Fetch refactored code from backend
        const fetchRefactoredCode = async () => {
            try {
                // This is where the actual API call would go
                // const response = await fetch('/api/refactor', {
                //   method: 'POST',
                //   headers: { 'Content-Type': 'application/json' },
                //   body: JSON.stringify({
                //     originalCode,
                //     fileName: originalFileName,
                //     model: modelSelected,
                //     promptType
                //   })
                // });

                // if (!response.ok) throw new Error('Failed to refactor code');
                // const data = await response.json();

                // Mock response for development
                const mockData: RefactoredData = {
                    originalCode: originalCode,
                    refactoredCode: `interface Workable {
  void work();
}

interface Eatable {
  void eat();
}

interface Sleepable {
  void sleep();
}

class Robot implements Workable {
  @Override
  public void work() {
      System.out.println("Robot is working...");
  }
}

class Human implements Workable, Eatable, Sleepable {
  @Override
  public void work() {
      System.out.println("Human is working...");
  }
  
  @Override
  public void eat() {
      System.out.println("Human is eating...");
  }
  
  @Override
  public void sleep() {
      System.out.println("Human is sleeping...");
  }
}`,
                    codeChanges: [
                        { lineNumber: 1, explanation: "Created 'Workable' interface to focus on work-related functionality only" },
                        { lineNumber: 5, explanation: "Created 'Eatable' interface for eating functionality" },
                        { lineNumber: 9, explanation: "Created 'Sleepable' interface for sleeping functionality" },
                        { lineNumber: 13, explanation: "Modified 'Robot' class to only implement 'Workable' interface following Single Responsibility Principle" },
                        { lineNumber: 20, explanation: "Created new 'Human' class that implements all interfaces, properly separating concerns" }
                    ],
                    executionTime: "2.3s",
                    modelUsed: modelSelected
                };

                console.log("Received refactored code from backend:", mockData);

                // Simulate a delay for development
                setTimeout(() => {
                    clearInterval(dotsInterval);
                    onLoadingComplete(mockData);
                }, 10000);

            } catch (err) {
                console.error("Error refactoring code:", err);
                clearInterval(dotsInterval);
                onError("Failed to refactor code. Please try again.");
            }
        };

        // Start the fetch process immediately
        fetchRefactoredCode();

        return () => {
            clearInterval(dotsInterval);
        };
    }, [isLoading, originalCode, originalFileName, modelSelected, promptType, onLoadingComplete, onError]);

    if (!isLoading) return null;

    return (
        <div className="fixed inset-0 flex flex-col items-center justify-center bg-[#606b50] bg-opacity-95 z-50">
            {/* Dino GIF */}
            <div className="w-64 h-64 mb-6">
                <img
                    src="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/dbc34067-fa60-4cfe-90b4-3355a7495a46/dduu97f-aa48c62a-8d27-4176-948b-c51ce8775929.gif?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcL2RiYzM0MDY3LWZhNjAtNGNmZS05MGI0LTMzNTVhNzQ5NWE0NlwvZGR1dTk3Zi1hYTQ4YzYyYS04ZDI3LTQxNzYtOTQ4Yi1jNTFjZTg3NzU5MjkuZ2lmIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.JWYyHS4tfnZbrADvIiYmBuSM5B1hNUuCNDC1o91lfr4"
                    alt="Running Dinosaur"
                    className="w-full h-full object-contain"
                />
            </div>

            <div className="mt-4 text-white text-lg font-medium">
                Refactoring{dots}
            </div>
            <div className="mt-2 text-white/70 text-sm">
                Using {modelSelected} model with {promptType} prompt
            </div>
        </div>
    );
};

export default LoadingScreen;