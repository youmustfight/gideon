import { useEffect } from "react";
import { EditorState, LexicalEditor } from "lexical";
import { LexicalComposer } from "@lexical/react/LexicalComposer";
import { RichTextPlugin } from "@lexical/react/LexicalRichTextPlugin";
import { ContentEditable } from "@lexical/react/LexicalContentEditable";
import { HistoryPlugin } from "@lexical/react/LexicalHistoryPlugin";
import { OnChangePlugin } from "@lexical/react/LexicalOnChangePlugin";
import { AutoFocusPlugin } from "@lexical/react/LexicalAutoFocusPlugin";
import LexicalErrorBoundary from "@lexical/react/LexicalErrorBoundary";
import { HeadingNode, QuoteNode } from "@lexical/rich-text";
import { TableCellNode, TableNode, TableRowNode } from "@lexical/table";
import { ListItemNode, ListNode } from "@lexical/list";
import { CodeHighlightNode, CodeNode } from "@lexical/code";
import { LinkNode } from "@lexical/link";
import { LinkPlugin } from "@lexical/react/LexicalLinkPlugin";
import { ListPlugin } from "@lexical/react/LexicalListPlugin";
import { MarkdownShortcutPlugin } from "@lexical/react/LexicalMarkdownShortcutPlugin";
import { TRANSFORMERS } from "@lexical/markdown";
import { $generateHtmlFromNodes } from "@lexical/html";

import { ToolbarPlugin } from "./plugins/ToolbarPlugin";
import { LoadHtmlPlugin } from "./plugins/LoadHtmlPlugin";
import {
  StyledWritingEditorCSS,
  StyledWritingEditorDropdownCSS,
  StyledWritingEditorLinkEditCSS,
  WritingEditorTheme,
} from "./WritingEditorTheme";

type TWriterEditor = {
  html?: string;
  onChange: (data: { html: string; text: string }) => void;
  onDownload: (type: "docx" | "pdf") => void;
};

// TODO: import/export HTML https://stackoverflow.com/questions/73094258/setting-editor-from-html
export const WritingLexicalEditor: React.FC<TWriterEditor> = ({ html, onChange, onDownload }) => {
  // MOUNT
  // --- HTML -> Lexical
  useEffect(() => {
    // TODO
  }, []);
  // --- Lexical -> HTML
  const onEditorChange = (editorState: EditorState, editor: LexicalEditor) => {
    // TODO: an update gets triggered when this component mounts
    editor.update(() => {
      const raw = $generateHtmlFromNodes(editor, null);
      onChange({
        html: raw,
        text: new DOMParser().parseFromString(raw, "text/html").documentElement.textContent ?? "",
      });
    });
  };

  // RENDER
  return (
    <>
      <div id="writing-editor-root">
        <StyledWritingEditorCSS />
        <StyledWritingEditorDropdownCSS />
        <StyledWritingEditorLinkEditCSS />
        <LexicalComposer
          initialConfig={{
            namespace: "writing-editor",
            // The editor theme
            theme: WritingEditorTheme,
            // Handling of errors during update
            onError(error) {
              throw error;
            },
            // Any custom nodes go here
            nodes: [
              HeadingNode,
              ListNode,
              ListItemNode,
              QuoteNode,
              CodeNode,
              CodeHighlightNode,
              TableNode,
              TableCellNode,
              TableRowNode,
              LinkNode,
            ],
          }}
        >
          <div className="editor-container">
            {/* TODO:  */}
            <ToolbarPlugin onDownloadDocx={() => onDownload("docx")} onDownloadPdf={() => onDownload("pdf")} />
            <div className="editor-inner">
              <RichTextPlugin
                contentEditable={<ContentEditable className="editor-input" />}
                placeholder={<div className="editor-placeholder">Enter some rich text...</div>}
                ErrorBoundary={LexicalErrorBoundary}
              />
              <LoadHtmlPlugin html={html} />
              <OnChangePlugin ignoreSelectionChange onChange={onEditorChange} />
              <HistoryPlugin />
              {/* <TreeViewPlugin /> */}
              <AutoFocusPlugin />
              <ListPlugin />
              <LinkPlugin />
              <MarkdownShortcutPlugin transformers={TRANSFORMERS} />
            </div>
          </div>
        </LexicalComposer>
      </div>
      <div></div>
    </>
  );
};
