import React from "react";
import { Link } from "react-router-dom";
import styled from "styled-components";
import { useHighlights } from "../data/useHighlights";

export const HighlightsBox: React.FC = ({ filename }: { filename?: string }) => {
  const { data } = useHighlights();
  const highlights = data?.filter((hl) => {
    if (filename) return hl.filename === filename;
    return true;
  });

  // RENDER
  return (
    <StyledHighlightsBox>
      {highlights?.map((hl) => (
        <div className="highlight">
          <div className="highlight__header">
            <small>
              <Link to={`/document/${hl.filename}#sentence-index-${hl.document_text_vectors_by_sentence_start_index}`}>
                {hl.filename}
              </Link>
            </small>
            <small>by: {hl.user}</small>
          </div>
          <div className="highlight__note">
            <p>{hl.note_text}</p>
          </div>
          <div className="highlight__highlight">
            <p>"...{hl.highlight_text}..."</p>
          </div>
        </div>
      ))}
    </StyledHighlightsBox>
  );
};

const StyledHighlightsBox = styled.div`
  .highlight {
    background: #ffffcf;
    border-radius: 4px;
    margin-bottom: 12px;
  }
  .highlight__header {
    display: flex;
    justify-content: space-between;
    padding: 12px 12px 4px;
    font-size: 12px;
  }
  .highlight__note {
    padding: 4px 12px;
    font-size: 14px;
    font-weight: 900;
  }
  .highlight__highlight {
    padding: 12px;
    font-size: 10px;
    font-style: italic;
  }
`;
