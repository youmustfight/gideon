import axios from "axios";
import { isBefore, subSeconds } from "date-fns";
import { capitalize } from "lodash";
import React, { useState } from "react";
import { Link } from "react-router-dom";
import styled from "styled-components";
import { TDocument, useDocuments } from "../data/useDocuments";

const DocumentBox: React.FC = ({ document }: { document: TDocument }) => {
  const [viewMore, setViewMore] = useState(false);
  return (
    <div className="discovery-box__document">
      <small>
        <Link to={`/document/${document.filename}`}>{document.filename ?? "n/a"}</Link> (
        {document?.format === "audio" ? (
          <>{document?.document_text_by_minute?.length} minutes</>
        ) : (
          <>{document?.document_text_by_page?.length} pages</>
        )}
        )
      </small>
      {["audio", "pdf"].includes(document.format) ? (
        <>
          <p>{document.document_type}</p>
          {viewMore ? (
            <>
              <div className="discovery-box__document__actions">
                <div>
                  <small onClick={() => setViewMore(false)}>Hide summary...</small>
                </div>
              </div>
              <div className="discovery-box__document__expanded">
                <p>
                  <u>Mentions</u>: {document.mentions_people?.filter((p) => p.length < 100)?.join(", ")}
                </p>
                <p>
                  <u>Summary</u>: {document.document_summary}
                </p>
              </div>
            </>
          ) : (
            <div className="discovery-box__document__actions">
              <div>
                <small onClick={() => setViewMore(true)}>View summary...</small>
              </div>
            </div>
          )}
        </>
      ) : null}
      {["image"].includes(document.format) ? (
        <p>
          {capitalize(document.document_type)}. {capitalize(document.document_summary)}.
        </p>
      ) : null}
    </div>
  );
};

export const DiscoveryBox = () => {
  const { data: documents = [] } = useDocuments();
  const [lastUploadedFileAt, setLastUploadedFileAt] = useState<Date>();
  const [isAddingFile, setIsAddingFile] = useState(false);
  const onSubmitFile = (type: "audio" | "image" | "pdf") => (e) => {
    e.preventDefault();
    if (e.target.file?.files?.[0]) {
      // --- setup form data/submit
      const formData = new FormData();
      formData.append("file", e.target.file.files[0]);
      axios.post(`http://localhost:3000/documents/index/${type}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      // --- clear file in input if successful
      e.target.file.value = "";
      setLastUploadedFileAt(new Date());
    }
  };

  // RENDER
  return (
    <StyledDiscoveryBox>
      <ul>
        {documents.map((doc) => (
          <li key={doc.filename}>
            <DocumentBox document={doc} />
          </li>
        ))}
        {lastUploadedFileAt && isBefore(new Date(), subSeconds(lastUploadedFileAt, 15)) ? (
          <li>
            <div className="discovery-box__document processing">
              <p>File processing. Will appear soon above...</p>
            </div>
          </li>
        ) : null}
      </ul>

      {isAddingFile ? (
        <>
          {/* PDF */}
          <form className="discovery-box__file-uploader" onSubmit={onSubmitFile("pdf")}>
            <input type="file" name="file" accept=".pdf" />
            <button type="submit">Upload PDF</button>
          </form>

          {/* IMAGE */}
          <form className="discovery-box__file-uploader" onSubmit={onSubmitFile("image")}>
            <input type="file" name="file" accept=".jpg,.jpeg,.png" />
            <button type="submit">Upload Image</button>
          </form>

          {/* AUDIO */}
          <form className="discovery-box__file-uploader" onSubmit={onSubmitFile("audio")}>
            <input type="file" name="file" accept=".m4a,.mp3" />
            <button type="submit">Upload Audio</button>
          </form>
        </>
      ) : (
        <button className="add-files-btn" onClick={() => setIsAddingFile(true)}>
          + PDF, Audio, Video
        </button>
      )}
    </StyledDiscoveryBox>
  );
};

const StyledDiscoveryBox = styled.div`
  p {
    font-size: 14px;
    margin: 0;
    margin-top: 4px;
  }
  small {
    margin: 4px 0;
    font-size: 12px;
  }
  & > ul {
    padding-left: 0 !important;
    list-style-type: none !important;
  }
  li {
    margin: 4px 0;
    & > div {
      padding: 4px;
    }
  }
  .discovery-box__document {
    background: white;
    border-radius: 4px;
    padding: 8px 12px 8px;
    margin: 4px 0;
    &.processing {
      opacity: 0.5;
      text-align: center;
      margin-bottom: 6px;
      margin-top: 0;
    }
  }
  .discovery-box__document__expanded {
    border-top: 1px solid #eee;
    margin-top: 2px;
  }
  .discovery-box__document__actions {
    border-top: 1px solid #eee;
    margin-top: 2px;
    small {
      cursor: pointer;
    }
  }
  .discovery-box__file-uploader {
    width: 100%;
    display: flex;
    justify-content: space-between;
    margin-top: 16px;
  }
  .add-files-btn {
    width: 100%;
    text-align: center;
    margin-top: 8px;
  }
`;
