"use client";

import { useRef } from "react";
import Editor from "@monaco-editor/react";
import type * as monaco from "monaco-editor";

interface CodeEditorProps {
  value: string;
  onChange?: (value: string | undefined) => void;
  language?: string;
}

export default function CodeEditor({ value, onChange, language = "java" }: CodeEditorProps) {
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);

  return (
    <div className="h-full w-full overflow-hidden">
      <Editor
        height="100%"
        width="100%"
        theme="vs-dark"
        language={language}
        value={value}
        onChange={onChange}
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