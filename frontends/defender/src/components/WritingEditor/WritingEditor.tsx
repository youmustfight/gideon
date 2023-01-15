import axios from "axios";
import saveAs from "file-saver";
import { snakeCase } from "lodash";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useDebounce } from "react-use";
import { useWriting, useWritingUpdate } from "../../data/useWriting";
import { TWriting } from "../../data/useWritings";
import { WritingLexicalEditor } from "./WritingLexicalEditor";

type TWritingEditorProps = {
  writingId: number;
};

export const WritingEditor: React.FC<TWritingEditorProps> = ({ writingId }) => {
  const { data: writing, isSuccess: isSuccessWriting } = useWriting(writingId);
  const { mutateAsync: writingUpdate } = useWritingUpdate();
  // HELPERS
  // --- docx
  const onDownloadDocx = () => {
    axios({ method: "get", url: `/v1/writing/${writingId}/docx`, responseType: "blob" }).then((res) =>
      saveAs(res.data, `${snakeCase(writing!.name)}.docx`)
    );
  };
  // --- pdf
  const onDownloadPdf = () => {
    window.open(`/writing/${writingId}/pdf`, "_blank");
  };

  // MOUNT
  // --- writing props
  const [editorChange, setEditorChange] = useState<{ html: string; text: string }>();
  useDebounce(() => writingUpdate({ ...writing, body_html: editorChange?.html, body_text: editorChange?.text }), 1000, [
    editorChange,
  ]);

  // RENDER
  return isSuccessWriting && writing ? (
    <WritingLexicalEditor
      html={writing.body_html}
      onChange={({ html, text }) => {
        setEditorChange({ html, text });
      }}
      onDownload={(type) => {
        if (type === "docx") onDownloadDocx();
        if (type === "pdf") onDownloadPdf();
      }}
    />
  ) : null;
};
