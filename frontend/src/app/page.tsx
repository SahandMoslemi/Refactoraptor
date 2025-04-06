"use client";

import { useState } from "react";
import CodeEditorTabs from "./components/CodeEditorTabs";

type FileProp = {
  name: string;
  language: string;
  content: string;
};

export default function Home() {
  const [files, setFiles] = useState<FileProp[]>([]);
  const [activeFile, setActiveFile] = useState<FileProp | null>(null);
  const [showIcons, setShowIcons] = useState(true);

  const handleFileUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
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
      setActiveFile(filePropArray[0]);
      setShowIcons(false); // Hide icons after uploading
    }
  };

  const handleWriteCode = () => {
    setShowIcons(false); // Hide icons on click
    alert("Write Code Clicked");
  };

  return (
    <div className="flex flex-col min-h-screen">
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
      <div className="flex-grow flex justify-center items-center ">
        <main className="flex flex-col items-center gap-10 ">
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
  
          {/* Code Editor Tabs */}
          {files.length > 0 && (
            <CodeEditorTabs files={files} activeFile={activeFile} />
          )}
        </main>
      </div>
    </div>
  );
  
}
