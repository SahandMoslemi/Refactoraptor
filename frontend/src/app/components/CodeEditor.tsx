"use client";

import { useRef } from "react";
import Editor from "@monaco-editor/react";
import type * as monaco from "monaco-editor";

interface CodeEditorProps {
  value: string;
  onChange?: (value: string) => void;
  language?: string;
}

export default function CodeEditor({
  value,
  onChange,
  language = "java",
}: CodeEditorProps) {
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);

  // This handler safely bridges between Monaco's type and your expected type
  const handleEditorChange = (value: string | undefined) => {
    // Only call onChange if both onChange exists and value is defined
    if (onChange && value !== undefined) {
      onChange(value);
    }
  };

  return (
    <div className="h-full w-full overflow-hidden">
      <Editor
        height="100%"
        theme="vs-dark"
        language={language}
        value={value}
        onChange={handleEditorChange}
        onMount={(editor) => {
          editorRef.current = editor;
        }}
        options={{
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          fontSize: 14,
          lineNumbers: "on",
          roundedSelection: false,
          renderLineHighlight: "line",
          automaticLayout: true,
        }}
      />
    </div>
  );
}
