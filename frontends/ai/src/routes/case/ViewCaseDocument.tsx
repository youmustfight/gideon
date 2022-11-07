import React, { useEffect, useState } from "react";
import { Link, useLocation, useMatch } from "react-router-dom";
import styled from "styled-components";
import { HighlightsBox } from "../../components/HighlightsBox";
import { useHighlightStore } from "../../data/HighlightStore";
import { useTeamStore } from "../../data/TeamStore";
import { useDocument } from "../../data/useDocument";
import { TDocument, TDocumentContent, TDocumentSentenceTextVector, useDocuments } from "../../data/useDocuments";
import { useHighlights } from "../../data/useHighlights";

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

const DocumentViewTranscript = ({ document: doc }: { document: TDocument }) => {
  const { hash } = useLocation();
  // const { setSentenceStartIndex, setSentenceEndIndex } = useHighlightStore();
  // ON MOUNT
  // useEffect(() => {
  //   // --- reset sentence highlight selections
  //   setSentenceStartIndex(null);
  //   setSentenceEndIndex(null);
  // }, []);
  useEffect(() => {
    // --- scroll if we had an #anchor link param
    setTimeout(() => {
      if (hash !== "" && typeof document !== "undefined" && document?.querySelector != null) {
        const element = document.querySelector(hash);
        if (element) element.scrollIntoView();
      }
    });
  }, [hash]);
  const documentTextByPage =
    doc.content.reduce((accum, dc) => {
      // don't push document content that is max chunks. that doesn't consider page
      if (dc.tokenizing_strategy === "sentence") {
        if (!accum[dc.page_number]) accum[dc.page_number] = [];
        accum[dc.page_number].push(dc);
      }
      return accum;
    }, {}) ?? {};

  // RENDER
  return (
    <StyledDocumentViewTranscript>
      {Object.keys(documentTextByPage)?.map((pageNumber) => (
        <div
          key={`source-text-${pageNumber}`}
          id={`source-text-${pageNumber}`}
          className={hash && Number(hash?.replace(/[^0-9]/g, "")) === pageNumber ? "active" : ""}
        >
          <div className="document-transcript__header">
            <h6>Page #{pageNumber}:</h6>
            <hr />
          </div>
          {/* <p>{doc.document_text_by_minute}</p> */}
          <p>
            {documentTextByPage[pageNumber].map((documentContent) => (
              <>{documentContent.text}</>
            ))}
          </p>
        </div>
      ))}
      {/* TODO: need to fix up audio indexing first */}
      {/* {doc.document_text_by_minute?.map((minuteText, index) => (
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
      ))} */}
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
  const { caseId, documentId } = useMatch("/case/:caseId/document/:documentId")?.params;
  const { data: document } = useDocument(documentId);
  // const { data: highlights = [] } = useHighlights();
  // TODO: need to get content, file, highlights loaded in
  const hasHighlights = false; // TODO: refactor highlights.some((hl) => hl.filename === filename);

  // RENDER
  return !document ? null : (
    <div>
      {/* SUMMARY */}
      <div className="section-lead">
        <h4>
          <Link to={`/case/${caseId}`}>
            <button>←</button>
          </Link>{" "}
          <span>{document?.name}</span>
        </h4>
        <br />
        <h2>{document?.document_type}</h2>
        {document.type === "audio" ? (
          <div>
            <audio src={document?.[files]?.[0] ?? ""} controls type="audio/mpeg"></audio>
          </div>
        ) : null}
      </div>
      <section>
        <DocumentViewSummary document={document} />
        {/* TODO */}
        {/* {document.mentions_people?.length > 0 ? (
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
        ) : null} */}
      </section>

      {/* HIGHLIGHTS */}
      {/* TODO */}
      {/* {hasHighlights ? (
        <>
          <div className="section-lead">
            <h4>Highlights</h4>
          </div>
          <section>
            <HighlightsBox filename={document.filename} />
          </section>
        </>
      ) : null} */}

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
