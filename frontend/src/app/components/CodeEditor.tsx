"use client";

import { useRef } from "react";
import Editor from "@monaco-editor/react";
import type * as monaco from "monaco-editor";

interface CodeEditorProps {
  language: string;
  value: string;
}

export default function CodeEditor({ language, value }: CodeEditorProps) {
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);

  return (
    <Editor
      height="66vh"
      theme="vs-dark"
      language={language}
      value={value}
      onMount={(editor) => {
        editorRef.current = editor;
      }}
    />
  );
}