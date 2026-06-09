"use client";

import Editor from "@monaco-editor/react";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

export default function CodeEditor({ value, onChange }: Props) {
  return (
    <div className="editor-frame">
      <Editor
        height="320px"
        language="python"
        theme="vs-dark"
        value={value}
        onChange={(v) => onChange(v ?? "")}
        options={{
          fontSize: 14,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          tabSize: 4,
          insertSpaces: true,
          wordWrap: "on",
          automaticLayout: true,
        }}
      />
    </div>
  );
}
