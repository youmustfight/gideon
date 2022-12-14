import React from "react";
import { useMatch } from "react-router-dom";
import styled from "styled-components";
import { useWriting } from "../../data/useWriting";
import { PdfPreview } from "../../components/PdfPreview";

export const ViewWritingPDF = () => {
  const { writingId } = useMatch("/writing/:writingId/pdf")?.params;
  const { data: writing } = useWriting(writingId);
  // RENDER
  return (
    <StyledViewWritingPDF>
      <PdfPreview html={writing?.body_html} />
    </StyledViewWritingPDF>
  );
};

const StyledViewWritingPDF = styled.div`
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
  bottom: 0;
`;
