// @ts-nocheck

import { useState } from "react";
import styled from "styled-components";
import { useHighlightStore } from "../../data/deprecated/HighlightStore";
import { useAppStore } from "../../data/AppStore";
import { TDocument, TDocumentSentenceTextVector } from "../../data/useDocuments";
import { useHighlights } from "../../data/deprecated/useHighlights";

const SentenceTextVector = ({
  document,
  textVector,
  textVectorIndex,
}: {
  document: TDocument;
  textVector: TDocumentSentenceTextVector;
  textVectorIndex: number;
}) => {
  const { currentUser } = useAppStore();
  const { data: highlights } = useHighlights();
  // SETUP
  const [isHovering, setIsHovering] = useState(false);
  const {
    sentenceEndIndex,
    sentenceStartIndex,
    setSentenceStartIndex,
    setSentenceEndIndex,
    hightlightNoteText,
    setHightlightNoteText,
    saveHighlightAndOpinion,
  } = useHighlightStore();
  const isHighlighted = sentenceEndIndex === textVectorIndex || sentenceStartIndex === textVectorIndex;
  const isBetweenHighlighted =
    sentenceEndIndex != null &&
    sentenceStartIndex != null &&
    textVectorIndex < sentenceEndIndex &&
    textVectorIndex > sentenceStartIndex;
  const wasHighlighted = highlights?.some(
    (hl) =>
      hl.filename === document.name &&
      textVectorIndex >= hl.document_text_vectors_by_sentence_start_index &&
      textVectorIndex <= hl.document_text_vectors_by_sentence_end_index
  );
  // RENDER
  return (
    <>
      <StyledSentenceTextVector
        id={`sentence-index-${textVectorIndex}`}
        className={`${isHovering ? "hovering" : ""} ${wasHighlighted ? "was-highlighted" : ""} ${
          isHighlighted || isBetweenHighlighted ? "highlighted" : ""
        }`}
        onMouseEnter={() => setIsHovering(true)}
        onMouseLeave={() => setIsHovering(false)}
      >
        {textVector.text}
        {"."}
        {isHovering ? (
          <>
            <button onClick={() => setSentenceStartIndex(textVectorIndex)}>🖊→</button>
            <button onClick={() => setSentenceEndIndex(textVectorIndex)}>←🖊</button>
          </>
        ) : null}
      </StyledSentenceTextVector>
      {sentenceEndIndex === textVectorIndex ? (
        <StyledSentenceTextVectorHighlightForm
          onSubmit={(e) => {
            e.preventDefault();
            if (sentenceStartIndex != null && sentenceEndIndex != null) {
              saveHighlightAndOpinion({
                filename: document.name,
                user: currentUser,
                document_text_vectors_by_sentence_start_index: sentenceStartIndex,
                document_text_vectors_by_sentence_end_index: sentenceEndIndex,
                highlight_text: document.document_text_vectors_by_sentence
                  .slice(sentenceStartIndex, sentenceEndIndex)
                  .map((tv) => tv.text)
                  .join("."),
                note_text: hightlightNoteText,
              });
            }
          }}
        >
          <textarea value={hightlightNoteText} onChange={(e) => setHightlightNoteText(e.target.value)}></textarea>
          <button type="submit" disabled={hightlightNoteText?.length === 0}>
            Save Highlight & Opinion
          </button>
        </StyledSentenceTextVectorHighlightForm>
      ) : null}
    </>
  );
};

const StyledSentenceTextVectorHighlightForm = styled.form`
  display: flex;
  flex-direction: column;
  button {
    font-size: 12px;
  }
`;

const StyledSentenceTextVector = styled.span`
  button {
    font-size: 6px;
  }
  &.hovering {
    text-decoration: underline;
  }
  &.was-highlighted {
    background: #ffffcf;
  }
  &.highlighted {
    background: yellow;
  }
`;
