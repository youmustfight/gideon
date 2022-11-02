import React, { useEffect, useState } from "react";
import { Link, useLocation, useMatch } from "react-router-dom";
import styled from "styled-components";
import { HighlightsBox } from "../../components/HighlightsBox";
import { useHighlightStore } from "../../data/HighlightStore";
import { useTeamStore } from "../../data/TeamStore";
import { TDocument, TDocumentSentenceTextVector, useDocuments } from "../../data/useDocuments";
import { useHighlights } from "../../data/useHighlights";

// HACK: Urls for files I chucked in notion if we want to simulate files
const temporaryStaticFileUrls = {
  "merrick-garland-press-conference-mar-a-lago.m4a":
    "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/def94528-5ffe-478d-8241-6fe6ad401a6f/merrick-garland-press-conference-mar-a-lago.m4a?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220928%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220928T224600Z&X-Amz-Expires=86400&X-Amz-Signature=38ae3fb3d8b4e9c5ef6903771242c7999a4b141bfb5303101d8841e8a82e94b5&X-Amz-SignedHeaders=host&x-id=GetObject",
};

const DocumentViewSummary = ({ document }: { document: TDocument }) => {
  const [isFullyVisible, setIsFullyVisible] = useState(false);
  return (
    <StyledDocumentViewSummary>
      <p>
        {isFullyVisible ? document.document_summary : document.document_summary?.slice(0, 400)}{" "}
        <u onClick={() => setIsFullyVisible(!isFullyVisible)}>{isFullyVisible ? "...Hide more" : "...Show more"}</u>
      </p>
    </StyledDocumentViewSummary>
  );
};

const StyledDocumentViewSummary = styled.div`
  padding: 4px;
  font-size: 13px;
  line-height: 115%;
  u {
    cursor: pointer;
  }
`;

const SentenceTextVector = ({
  document,
  textVector,
  textVectorIndex,
}: {
  document: TDocument;
  textVector: TDocumentSentenceTextVector;
  textVectorIndex: number;
}) => {
  const { currentUser } = useTeamStore();
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
      hl.filename === document.filename &&
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
                filename: document.filename,
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

const DocumentViewTranscript = ({ document: doc }: { document: TDocument }) => {
  const { hash } = useLocation();
  const { setSentenceStartIndex, setSentenceEndIndex } = useHighlightStore();
  // ON MOUNT
  useEffect(() => {
    // --- reset sentence highlight selections
    setSentenceStartIndex(null);
    setSentenceEndIndex(null);
  }, []);
  useEffect(() => {
    // --- scroll if we had an #anchor link param
    setTimeout(() => {
      if (hash !== "" && typeof document !== "undefined" && document?.querySelector != null) {
        const element = document.querySelector(hash);
        if (element) element.scrollIntoView();
      }
    });
  }, [hash]);

  // RENDER
  return (
    <StyledDocumentViewTranscript>
      {doc.document_text_by_page?.map((pageText, pageIndex) => (
        <div
          key={`source-text-${pageIndex + 1}`}
          id={`source-text-${pageIndex + 1}`}
          className={hash && Number(hash?.replace(/[^0-9]/g, "")) === pageIndex + 1 ? "active" : ""}
        >
          <div className="document-transcript__header">
            <h6>Page #{pageIndex + 1}:</h6>
            <hr />
          </div>
          {/* <p>{doc.document_text_by_minute}</p> */}
          <p>
            {doc.document_text_vectors_by_sentence.map((tv, tvIndex) => (
              <>
                {/* DONT FILTER BC WE NEED TO PRESERVE TV ARR INDEX FOR SELECTING ACROSS PAGES */}
                {tv.page_number === pageIndex + 1 ? (
                  <SentenceTextVector document={doc} textVector={tv} textVectorIndex={tvIndex} />
                ) : null}
              </>
            ))}
          </p>
        </div>
      ))}
      {doc.document_text_by_minute?.map((minuteText, index) => (
        <div
          key={`source-text-${index}`}
          id={`source-text-${index}`}
          className={hash && Number(hash?.replace(/[^0-9]/g, "")) === index ? "active" : ""}
        >
          <div className="document-transcript__header">
            <h6>Minute {index}:</h6>
            <hr />
            <button>▶️</button>
          </div>
          <p>{minuteText}</p>
        </div>
      ))}
    </StyledDocumentViewTranscript>
  );
};

const StyledDocumentViewTranscript = styled.div`
  & > div {
    margin: 8px 0;
    padding: 8px;
    border-radius: 4px;
    &.active {
      background: #ffffcf;
    }
    h6 {
      margin-bottom: 8px;
      text-deocration: underline;
      font-style: italic;
      font-size: 12px;
    }
    p {
      font-size: 13px;
      line-height: 115%;
    }
    .document-transcript__header {
      display: flex;
      align-items: center;
      hr {
        flex-grow: 1;
      }
    }
  }
`;

export const ViewCaseDocument = () => {
  const { caseId, filename } = useMatch("/case/:caseId/document/:filename")?.params;
  const { data: highlights = [] } = useHighlights();
  const { data: documents = [] } = useDocuments();
  const document = documents.find((d) => d.filename === filename);
  const hasHighlights = highlights.some((hl) => hl.filename === filename);

  // RENDER
  return !document ? null : (
    <div>
      {/* SUMMARY */}
      <div className="section-lead">
        <h4>
          <Link to={`/case/${caseId}`}>
            <button>←</button>
          </Link>{" "}
          <span>{document?.filename}</span>
        </h4>
        <br />
        <h2>{document?.document_type}</h2>
        {document.format === "audio" ? (
          <div>
            <audio src={temporaryStaticFileUrls[document.filename] ?? ""} controls type="audio/mpeg"></audio>
          </div>
        ) : null}
      </div>
      <section>
        <DocumentViewSummary document={document} />
        {document.mentions_people?.length > 0 ? (
          <>
            <small style={{ fontSize: "12px", fontWeight: "900" }}>Mentioned People</small>
            <ul>
              {document.mentions_people?.map((p) => (
                <li key={p} className="person-pill">
                  {p}
                </li>
              ))}
            </ul>
          </>
        ) : null}
        {document.event_timeline?.length > 0 ? (
          <>
            <small style={{ fontSize: "12px", fontWeight: "900" }}>Mentioned Timeline/Events</small>
            <ul>
              {document.event_timeline.map((str) => (
                <li key={str}>{str}</li>
              ))}
            </ul>
          </>
        ) : null}
      </section>

      {/* HIGHLIGHTS */}
      {hasHighlights ? (
        <>
          <div className="section-lead">
            <h4>Highlights</h4>
          </div>
          <section>
            <HighlightsBox filename={document.filename} />
          </section>
        </>
      ) : null}

      {/* OCR/TRANSCRIPTION TEXT BY PAGE/MINUTE */}
      <div className="section-lead">
        <h4>Source Text/Transcript</h4>
      </div>
      <section>
        <DocumentViewTranscript document={document} />
      </section>
    </div>
  );
};
