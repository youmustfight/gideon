import React, { useEffect, useState } from "react";
import { Link, useLocation, useMatch } from "react-router-dom";
import styled from "styled-components";
import { TDocument, useDocuments } from "./data/useDocuments";

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

const DocumentViewTranscript = ({ document: doc }: { document: TDocument }) => {
  console.log(doc);
  const { hash } = useLocation();
  // ON MOUNT
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
      {doc.document_text_by_page?.map((pageText, index) => (
        <div
          id={`source-text-${index + 1}`}
          className={hash && Number(hash?.replace(/[^0-9]/g, "")) === index + 1 ? "active" : ""}
        >
          <div className="document-transcript__header">
            <h6>Page #{index + 1}:</h6>
            <hr />
          </div>
          <p>{pageText}</p>
        </div>
      ))}
      {doc.document_text_by_minute?.map((minuteText, index) => (
        <div
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
        </h4>
        {document.format === "pdf" ? (
          <a href={temporaryStaticFileUrls[document.filename] ?? ""}>Download</a>
        ) : (
          <div>
            <audio src={temporaryStaticFileUrls[document.filename] ?? ""} controls type="audio/mpeg"></audio>
          </div>
        )}
        <h2>{document?.document_type}</h2>
      </div>
      <section>
        <DocumentViewSummary document={document} />
      </section>

      {/* PEOPLE */}
      {document.mentions_people?.length > 0 ? (
        <>
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
        </>
      ) : null}

      {/* TIMELINE */}
      {document.event_timeline?.length > 0 ? (
        <>
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
