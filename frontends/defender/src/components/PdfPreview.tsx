// INSPIRATION FROM:
// https://github.com/Aymkdn/html-to-pdfmake/blob/master/docs/index.html
// https://stackblitz.com/edit/react-pdfmake?file=Pdf.js
// https://github.com/bpampuch/pdfmake/issues/1757#issuecomment-509796905
// https://pdfmake.github.io/docs/0.1/document-definition-object/styling/
import React, { useEffect } from "react";
import htmlToPdfmake from "html-to-pdfmake";
import pdfMake from "pdfmake/build/pdfmake";
import pdfFonts from "pdfmake/build/vfs_fonts";
import styled from "styled-components";
pdfMake.vfs = pdfFonts.pdfMake.vfs;

export const PdfPreview = ({ html }) => {
  // ON HTML CHANGE
  useEffect(() => {
    // --- convert html to content stack
    const content = htmlToPdfmake(html, {
      tableAutoSize: true,
      customTag: (params) => {
        var ret = params.ret;
        var element = params.element;
        // TODO: figure out how to get alignment style, dir tags, or some className for header alignments
        return ret;
      },
    });
    // --- create document definition
    const documentDefinition = {
      pageSize: "LETTER",
      pageMargins: [100, 100, 100, 100],
      content,
      styles: {
        // HACK: when the style className is passed through from writing-editor, we know to underline
        "editor-text-underline": {
          decoration: "underline",
        },
      },
    };
    console.log("PdfPreview documentDefinition", documentDefinition);
    pdfMake.createPdf(documentDefinition).getDataUrl((dataStr) => {
      document.getElementById("pdfmake-iframe").src = dataStr;
    });
  }, [html]);

  return (
    <StyledPdfPreview>
      <iframe id="pdfmake-iframe"></iframe>
    </StyledPdfPreview>
  );
};

const StyledPdfPreview = styled.div`
  &,
  iframe {
    width: 100%;
    height: 100%;
  }
`;
