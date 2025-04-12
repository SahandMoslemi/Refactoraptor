"use client";

import { useState, useEffect } from "react";
import { FileData } from "../page";
import CodeEditor from "./CodeEditor";

type EditorWorkspaceProps = {
  files: FileData[];
  activeFileId: string | null;
  onFileChange: (fileId: string) => void;
  onCodeChange: (content: string) => void;
  toggleControlPanel: () => void;
};

export default function EditorWorkspace({
  files,
  activeFileId,
  onFileChange,
  onCodeChange,
  toggleControlPanel,
}: EditorWorkspaceProps) {
  // Animation state
  const [isExpanded, setIsExpanded] = useState(false);

  // Get the active file
  const activeFile =
    files.find((file) => file.id === activeFileId) || files[0] || null;

  // Trigger animation when component mounts
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsExpanded(true);
    }, 100); // Small delay for better animation effect

    return () => clearTimeout(timer);
  }, []);

  return (
    <div
      className="flex-grow flex justify-center items-center overflow-hidden"
      style={{ height: "66vh" }}
    >
      <div
        className={`bg-[#748569] rounded-l-md shadow-lg relative flex flex-col transition-all duration-500 ease-in-out ${
          isExpanded ? "w-full h-full" : "w-0 h-full"
        }`}
      >
        {/* File tabs */}
        {files.length > 0 && (
          <div className="flex text-gray-200 relative bg-[#505a46] flex-shrink-0">
            {files.map((file, index) => (
              <button
                key={file.id}
                onClick={() => onFileChange(file.id)}
                className={`px-4 py-2 text-sm transition-all ${
                  file.id === activeFileId
                    ? "bg-[#748569] text-white translate-y-[1px] shadow-inner z-20"
                    : "bg-[#3F4637] hover:bg-[#68765A]"
                } ${index === 0 ? "rounded-tl-md" : ""}`}
              >
                {file.name}
              </button>
            ))}
          </div>
        )}

        {/* Code editor */}
        <div
          className="p-1 relative flex-grow overflow-hidden"
          style={{ minHeight: "500px" }}
        >
          {activeFile && (
            <div className="absolute inset-1">
              <CodeEditor
                language={activeFile.language || ""}
                value={activeFile.content}
                onChange={onCodeChange}
              />
            </div>
          )}

          {/* Control panel toggle button */}
          <button
            className="absolute bottom-4 right-4 bg-[#3d4937] text-white w-10 h-10 rounded-full flex items-center justify-center opacity-70 hover:opacity-100 transition-opacity z-20 shadow-md"
            aria-label="Toggle Control Panel"
            onClick={toggleControlPanel}
          >
            <img
              src="/icons/format-icon.svg"
              alt="Format"
              className="w-6 h-6 invert"
            />
          </button>
        </div>
      </div>
    </div>
  );
}
