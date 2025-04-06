"use client";

import { useState, useEffect } from "react";
import CodeEditor from "./CodeEditor";

type FileProp = {
  name: string;
  language: string;
  content: string;
};

type Props = {
  files?: FileProp[];
  currentCode?: string;
  language?: string;
  activeFile?: FileProp | null;
  onTabChange?: (file: FileProp) => void;
  onChange?: (value: string) => void;
  onToggleControlPanel: () => void; // New prop to toggle control panel
};

export default function CodeEditorTabs({
                                         files = [],
                                         currentCode = '',
                                         language = 'java',
                                         activeFile = null,
                                         onTabChange,
                                         onChange,
                                         onToggleControlPanel
                                       }: Props) {
  const [currentFile, setCurrentFile] = useState<FileProp>(activeFile || (files.length > 0 ? files[0] : { name: 'New File', language, content: currentCode }));

  // Notify the parent component when the file changes
  useEffect(() => {
    if (onTabChange && currentFile) {
      onTabChange(currentFile);
    }
  }, [currentFile, onTabChange]);

  // Update when activeFile changes from outside
  useEffect(() => {
    if (activeFile && activeFile.name !== currentFile.name) {
      setCurrentFile(activeFile);
    }
  }, [activeFile]);

  const handleFileChange = (file: FileProp) => {
    setCurrentFile(file);
  };

  return (
      <div
          className="w-full h-full overflow-hidden relative flex flex-col"
          style={{ backgroundColor: "#748569" }}
      >
        {files.length > 0 && (
            <div
                className="flex text-gray-300 relative z-10 overflow-x-auto"
                style={{ backgroundColor: "#505a46" }}
            >
              {files.map((file, index) => (
                  <button
                      key={file.name}
                      onClick={() => handleFileChange(file)}
                      className={`px-4 py-2 text-sm transition-all whitespace-nowrap ${
                          currentFile.name === file.name
                              ? "bg-[#748569] text-white translate-y-[1px] shadow-inner z-20"
                              : "bg-[#3F4637] hover:bg-[#68765A]"
                      } ${index === files.length - 1 ? "rounded-tr-lg" : ""} `}
                  >
                    {file.name}
                  </button>
              ))}
            </div>
        )}

        <div className="flex-1 p-0 overflow-hidden relative">
          <CodeEditor
              language={files.length > 0 ? currentFile.language : language}
              value={files.length > 0 ? currentFile.content : currentCode}
              onChange={onChange}
          />

          {/* Format button in bottom right */}
          <button
              className="absolute bottom-4 right-4 bg-[#3d4937] text-white w-10 h-10 rounded-full flex items-center justify-center opacity-70 hover:opacity-100 transition-opacity"
              aria-label="Toggle Control Panel"
              onClick={onToggleControlPanel}
          >
            <img
                src="/icons/format-icon.svg"
                alt="Format"
                className="w-6 h-6"
            />
          </button>
        </div>
      </div>
  );
}