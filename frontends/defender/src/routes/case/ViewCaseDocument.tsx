import { orderBy } from "lodash";
import { Fragment, useEffect, useState } from "react";
import ReactPlayer from "react-player";
import { Link, useLocation, useMatch, useNavigate } from "react-router-dom";
import styled from "styled-components";
import { TimelineSummary } from "../../components/TimelineSummary";
import { reqDocumentEmbeddings, reqDocumentSummarize, useDocument } from "../../data/useDocument";
import { reqDocumentDelete } from "../../data/useDocumentDelete";
import { TDocument } from "../../data/useDocuments";

const DocumentViewImage = styled.div<{ imageSrc: string }>`
  width: 100%;
  min-height: 480px;
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  background-image: url(${(props) => props.imageSrc});
  margin-left: 6px;
`;

const DocumentViewSummary = ({ document }: { document: TDocument }) => {
  const [isFullyVisible, setIsFullyVisible] = useState(false);
  return (
    <StyledDocumentViewSummary>
      <p>
        {isFullyVisible ? document.document_summary : document.document_summary?.slice(0, 400)}{" "}
        <u onClick={() => setIsFullyVisible(!isFullyVisible)}>{isFullyVisible ? "...Hide more" : "...Show more"}</u>{" "}
      </p>
      {isFullyVisible ? (
        <>
          <br />
          <br />
          <div style={{ display: "flex" }}>
            <button onClick={() => reqDocumentSummarize(document.id)}>Re-run Summarizing Process</button>
            <button onClick={() => reqDocumentEmbeddings(document.id)}>Re-run Embeddings</button>
          </div>
        </>
      ) : null}
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
  h2,
  h4,
  h6 {
    font-weight: 900;
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
    setTimeout(() => {
      if (hash !== "" && typeof document !== "undefined" && document?.querySelector != null) {
        // --- scroll if we had an #anchor link param
        const element = document.querySelector(hash);
        if (element) element.scrollIntoView();
      } else {
        // --- otherwise scroll to top
        window.scrollTo(0, 0);
      }
    });
  }, [hash]);
  const documentTextByGrouping: Record<string, any[]> = (doc.content || []).reduce((accum, dc) => {
    // don't push document content that is max chunks. that doesn't consider page
    if (dc.tokenizing_strategy === "sentence") {
      if (doc.type === "pdf") {
        // @ts-ignore
        if (!accum[dc.page_number]) accum[dc.page_number] = [];
        // @ts-ignore
        accum[dc.page_number].push(dc);
      }
      if (["audio", "video"].includes(doc.type)) {
        // @ts-ignore
        const minute = Math.floor(dc.start_second / 60);
        // @ts-ignore
        if (!accum[minute]) accum[minute] = [];
        // @ts-ignore
        accum[minute].push(dc);
      }
    }
    return accum;
  }, {});

  // RENDER
  return (
    <StyledDocumentViewTranscript>
      {Object.keys(documentTextByGrouping)?.map((groupingNumber) => (
        <div
          key={`source-text-${groupingNumber}`}
          id={`source-text-${groupingNumber}`}
          className={hash && Number(hash?.replace(/[^0-9]/g, "")) === Number(groupingNumber) ? "active" : ""}
        >
          <div className="document-transcript__header">
            <h6>
              {doc.type === "pdf" ? "Page" : "▶️ Minute"} #{groupingNumber}:
            </h6>
            <hr />
          </div>
          {/* <p>{doc.document_text_by_minute}</p> */}
          <p>
            {documentTextByGrouping[groupingNumber].map((documentContent) => (
              <Fragment key={documentContent.id}>
                {" "}
                <span>{documentContent.text}</span>
              </Fragment>
            ))}
          </p>
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
  const navigate = useNavigate();
  // @ts-ignore
  const { caseId, documentId } = useMatch("/case/:caseId/document/:documentId")?.params;
  const { data: document } = useDocument(documentId);
  // --- highlights
  // const { data: highlights = [] } = useHighlights();
  // const hasHighlights = false; // TODO: refactor highlights.some((hl) => hl.filename === filename);
  // --- deletion
  const [isDeleting, setIsDeleting] = useState(false);
  const deleteHandler = async () => {
    setIsDeleting(true);
    await reqDocumentDelete(documentId);
    navigate(`/case/${caseId}`);
  };

  // RENDER
  return !document ? null : (
    <div>
      {/* SUMMARY */}
      <div className="section-lead">
        <h4>
          <Link to={`/case/${caseId}`}>
            <button>←</button>
          </Link>{" "}
          <span>Back to Documents</span>
        </h4>
        <br />
        <i>{document?.name}</i>
        <h2>{document?.document_description}</h2>
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

      {/* EVENTS */}
      {document.document_events && document.document_events?.length > 0 ? (
        <>
          <div className="section-lead">
            <h4>Timeline/Events</h4>
          </div>
          <section className="no-shadow">
            <TimelineSummary documentId={document.id} />
          </section>
        </>
      ) : null}

      {/* HIGHLIGHTS */}
      {/* TODO */}
      {/* {hasHighlights ? (
        <>
          <div className="section-lead">
            <h4>Highlights</h4>
          </div>
          <section>
            <HighlightsBox filename={document.name} />
          </section>
        </>
      ) : null} */}

      {/* AUDIO */}
      {document.type === "audio" ? (
        <>
          <div className="section-lead">
            <h4>Audio Player</h4>
          </div>
          <section>
            <audio src={document?.files?.[0]?.upload_url ?? ""} controls style={{ width: "100%" }}></audio>
          </section>
        </>
      ) : null}

      {/* VIDEO */}
      {document.type === "video" ? (
        <>
          <div className="section-lead">
            <h4>Video Player</h4>
          </div>
          <section>
            <ReactPlayer width="100%" height="100%" controls url={document?.files?.[0]?.upload_url} />
          </section>
        </>
      ) : null}

      {/* OCR/TRANSCRIPTION TEXT BY PAGE/MINUTE */}
      {document.type !== "image" && (
        <>
          <div className="section-lead">
            <h4>Source Text/Transcript</h4>
          </div>
          <section>
            <DocumentViewTranscript document={document} />
          </section>
        </>
      )}

      {/* IMAGE TEXT BY PAGE/MINUTE */}
      {document.type === "image" && document.files?.[0] && (
        <section>
          <DocumentViewImage imageSrc={document.files[0].upload_url} />
        </section>
      )}

      {/* DELETES */}
      <hr />
      <section>
        <button disabled={isDeleting} onClick={deleteHandler} style={{ width: "100%" }}>
          Delete Document
        </button>
      </section>
    </div>
  );
};
