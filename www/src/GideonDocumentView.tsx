import React, { useEffect } from "react";
import { Link, useLocation, useMatch } from "react-router-dom";
import styled from "styled-components";
import { TDocument, useDocuments } from "./data/useDocuments";

const DocumentViewSummary = ({ document }: { document: TDocument }) => {
  return (
    <StyledDocumentViewSummary>
      <p>{document.document_summary}</p>
    </StyledDocumentViewSummary>
  );
};

const StyledDocumentViewSummary = styled.div`
  padding: 4px;
  font-size: 13px;
  line-height: 115%;
`;

const DocumentViewTranscript = ({ document: doc }: { document: TDocument }) => {
  const { hash } = useLocation();
  // ON MOUNT --- scroll if we had an #anchor link param
  useEffect(() => {
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
      {doc.document_text_by_page?.map((pageText, index) => (
        <div
          id={`source-text-${index + 1}`}
          className={Number(hash?.replace(/[^0-9]/g, "")) === index + 1 ? "active" : ""}
        >
          <div className="document-transcript__header">
            <h6>Page #{index + 1}:</h6>
            <hr />
          </div>
          <p>{pageText}</p>
        </div>
      ))}
      {doc.document_text_by_minute?.map((minuteText, index) => (
        <div id={`source-text-${index}`} className={Number(hash?.replace(/[^0-9]/g, "")) === index ? "active" : ""}>
          <div className="document-transcript__header">
            <h6>Minute {index}:</h6>
            <hr />
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

export const GideonDocumentView = () => {
  // SETUP
  const paramFilename = useMatch("/document/:filename")?.params?.["filename"];
  const { data: documents = [] } = useDocuments();
  const document = documents.find((d) => d.filename === paramFilename);

  // RENDER
  return !document ? null : (
    <div>
      {/* SUMMARY */}
      <div className="section-lead">
        <h4>
          <Link to="/">🔙</Link> <span style={{ opacity: "0.3" }}>{document?.filename}</span>
          <br />
          <br />
          {document?.document_type}
        </h4>
      </div>
      <section>
        <DocumentViewSummary document={document} />
      </section>

      {/* PEOPLE */}
      <div className="section-lead">
        <h4>People</h4>
      </div>
      <section className="section-people">
        <ul>
          {document.mentions_people?.map((p) => (
            <li key={p} className="person-pill">
              {p}
            </li>
          ))}
        </ul>
      </section>

      {/* TIMELINE */}
      <div className="section-lead">
        <h4>Events, Timelines</h4>
      </div>
      <section>
        <div>
          <ul>
            {document.event_timeline.map((str) => (
              <li key={str}>{str}</li>
            ))}
          </ul>
        </div>
      </section>

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
