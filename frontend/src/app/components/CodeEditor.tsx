"use client";

import { Editor } from "@monaco-editor/react";

const CodeEditor = () => {
  return (
    <Editor
      height="50vh"
      width="75vh"
      theme="vs-dark"
      defaultLanguage="javascript"
    />
  );
};

export default CodeEditor;
