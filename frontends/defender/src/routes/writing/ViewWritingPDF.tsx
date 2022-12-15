import { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import styled from "styled-components";
import { useWriting } from "../../data/useWriting";
import { PdfPreview } from "../../components/PdfPreview";

export const ViewWritingPDF = () => {
  const navigate = useNavigate();
  const params = useParams();
  const writingId = Number(params.writingId);
  const { data: writing, isSuccess: isSuccessWriting } = useWriting(writingId);
  // ON MOUNT
  // --- check if we have a writing
  useEffect(() => {
    if (!writingId || (isSuccessWriting && !writing)) navigate("/");
  }, [writing, isSuccessWriting]);

  // RENDER
  return !writing ? null : (
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
