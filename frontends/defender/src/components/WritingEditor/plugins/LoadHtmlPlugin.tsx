// COPEID FROM https://github.com/facebook/lexical/issues/2452#issue-1274427993
import React, { useEffect } from "react";
import { $getRoot, $getSelection, RangeSelection } from "lexical";
import { useLexicalComposerContext } from "@lexical/react/LexicalComposerContext";
import { $generateHtmlFromNodes, $generateNodesFromDOM } from "@lexical/html";

export const LoadHtmlPlugin: React.FC<{ html?: string }> = ({ html }) => {
  const [editor] = useLexicalComposerContext();
  useEffect(() => {
    editor.update(() => {
      if (typeof html == "string") {
        const parser = new DOMParser();
        const dom = parser.parseFromString(html, "text/html");
        const nodes = $generateNodesFromDOM(editor, dom);
        // Select the root
        $getRoot().select();
        // Insert them at a selection.
        const selection = $getSelection() as RangeSelection;
        selection.insertNodes(nodes);
      }
    });
  }, [editor]);

  return null;
};
