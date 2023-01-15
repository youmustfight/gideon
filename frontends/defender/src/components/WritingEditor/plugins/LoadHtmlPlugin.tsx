// COPEID FROM https://github.com/facebook/lexical/issues/2452#issue-1274427993
import React, { useEffect } from "react";
import { $createParagraphNode, $getRoot, $getSelection, $insertNodes, RangeSelection } from "lexical";
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
        // HACK: a work around for a bug where if we don't start w/ a paragraph, lexical throws:
        // "Error: insertNodes: cannot insert a non-element into a root node"
        // https://github.com/facebook/lexical/issues/2308
        // selection.insertNodes(nodes);
        selection.insertNodes([$createParagraphNode(), ...nodes]);
      }
    });
  }, [editor]);

  return null;
};
