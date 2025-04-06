"use client";

import { useState } from "react";
import CodeEditor from "./CodeEditor";

type FileProp = {
  name: string;
  language: string;
  content: string;
};

type Props = {
  files: FileProp[];
  activeFile: FileProp | null;
};

export default function CodeEditorTabs({ files, activeFile }: Props) {
  const [currentFile, setCurrentFile] = useState<FileProp>(activeFile || files[0]);

  return (
    <div
      className="w-full overflow-hidden  mx-4 relative"
      style={{ backgroundColor: "#748569" , maxWidth:"50vw"}}
    >
      <div
        className="flex text-gray-300 relative z-10"
        style={{ backgroundColor: "#505a46" }}
      >
        {files.map((file, index) => (
          <button
            key={file.name}
            onClick={() => setCurrentFile(file)}
            className={`px-2 py-2 text-sm transition-all  ${
              currentFile.name === file.name
                ? "bg-[#748569] text-white translate-y-[1px] shadow-inner z-20"
                : "bg-[#3F4637] hover:bg-[#68765A]"
            } ${index === files.length - 1 ? "rounded-tr-lg" : ""} `}
          >
            {file.name}
          </button>
        ))}
      </div>

      <div className="p-1 flex justify-center">
        <CodeEditor
          language={currentFile.language}
          value={currentFile.content}
        />
      </div>
    </div>
  );
}
