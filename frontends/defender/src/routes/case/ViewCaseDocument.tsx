import { orderBy } from "lodash";
import { Fragment, useEffect, useState } from "react";
import ReactPlayer from "react-player";
import { Link, useLocation, useMatch, useNavigate } from "react-router-dom";
import styled from "styled-components";
import { getHashHighlightingSentenceStart, isHashHighlightingSentence } from "../../components/hashUtils";
import { TimelineSummary } from "../../components/TimelineSummary";
import { reqDocumentSummarize, useDocument } from "../../data/useDocument";
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
        const element = document.querySelector(`#${getHashHighlightingSentenceStart(hash)}`);
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
        const minute = Math.floor(dc.second_start / 60);
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
        <div key={`text-batch-${groupingNumber}`}>
          <div className="document-transcript__header">
            <h6>
              {doc.type === "pdf" ? "Page" : "▶️ Minute"} #{groupingNumber}:
            </h6>
            <hr />
          </div>
          {/* <p>{doc.document_text_by_minute}</p> */}
          <p>
            {documentTextByGrouping[groupingNumber].map((documentContent) => (
              <span
                key={`S${documentContent.id}`}
                id={`S${documentContent.sentence_number}`}
                className={isHashHighlightingSentence(hash, documentContent.sentence_number) ? "active" : ""}
              >
                {" "}
                {documentContent.text}
              </span>
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
    .active {
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
  // const {mutateAsync: updateDocument} = useDocumentUpdate();
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
    <StyledViewCaseDocument>
      {/* HEAD */}
      <div className="document-title">
        <h4>
          <b>{document.document_description}</b>
        </h4>
      </div>
      <div className="document-header">
        <Link to={`/case/${caseId}`}>
          <button>←</button>
        </Link>
        <input
          placeholder="Untitled Name"
          value={document?.name}
          disabled
          // onChange={(e) => writingUpdate({ id: writing.id, name: e.target.value })}
        />
      </div>

      {/* SUMMARY */}
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
            <ReactPlayer
              width="100%"
              height="100%"
              controls
              url={document?.files?.find((f) => f.mime_type?.includes("video"))?.upload_url}
            />
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
    </StyledViewCaseDocument>
  );
};

const StyledViewCaseDocument = styled.div`
  .document-title {
    text-align: center;
    padding: 20px 0 12px;
    font-weight: 900;
  }
  .document-header {
    padding: 0 24px;
    display: flex;
    & > a {
      max-width: 40px;
    }
    & > input {
      flex-grow: 1;
    }
    & > button {
      width: 150px;
      min-width: 150px;
      max-width: 150px;
    }
  }
`;
