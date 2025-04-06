"use client";

import { Editor } from "@monaco-editor/react";

interface CodeEditorProps {
    value: string;
    onChange?: (value: string | undefined) => void;
    language?: string;
}

const CodeEditor = ({ value, onChange, language = "java" }: CodeEditorProps) => {
    return (
        <div className="h-full w-full overflow-hidden">
            <Editor
                height="100%"
                width="100%"
                theme="vs-dark"
                defaultLanguage={language}
                value={value}
                onChange={onChange}
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
};

export default CodeEditor;