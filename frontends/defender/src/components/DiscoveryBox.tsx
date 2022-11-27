import axios from "axios";
import { isBefore, subSeconds } from "date-fns";
import { capitalize } from "lodash";
import React, { useState } from "react";
import ReactPlayer from "react-player";
import { Link, useMatch } from "react-router-dom";
import styled from "styled-components";
import { TDocument, useDocuments } from "../data/useDocuments";
import { getGideonApiUrl } from "../env";

const DocumentPreviewAudio = styled.audio`
  min-width: 120px;
  max-width: 120px;
  width: 120px;
`;
const DocumentPreviewImage = styled.div<{ imageSrc: string }>`
  min-width: 120px;
  max-width: 120px;
  width: 120px;
  height: 72px;
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  background-image: url(${(props) => props.imageSrc});
  margin-left: 6px;
`;

const DocumentBox: React.FC<{ document: TDocument }> = ({ document }) => {
  const [viewMore, setViewMore] = useState(false);
  const matches = useMatch("/case/:caseId/*");
  const caseId = Number(matches?.params?.caseId);
  const pageCount = Math.max(...Array.from(new Set(document?.content?.map((dc) => Number(dc.page_number)))));
  const minuteCount = Math.max(...Array.from(new Set(document?.content?.map((dc) => Number(dc.end_second)))));
  return (
    <div className="discovery-box__document">
      <div style={{ flexGrow: 1 }}>
        <small>
          <Link to={`/case/${caseId}/document/${document.id}`}>{document.name ?? "n/a"}</Link>
          {document?.type === "audio" ? <> ({minuteCount} minutes)</> : null}
          {document?.type === "pdf" ? <> ({pageCount} pages)</> : null}
        </small>
        {["audio", "pdf", "video"].includes(document.type) ? (
          <>
            <p>{document.document_description}</p>
            {viewMore ? (
              <>
                <div className="discovery-box__document__actions">
                  <div>
                    <small onClick={() => setViewMore(false)}>Hide summary...</small>
                  </div>
                </div>
                <div className="discovery-box__document__expanded">
                  <p>
                    <u>Mentions</u>: TODO
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
        {["image"].includes(document.type) ? (
          <p>
            {capitalize(document.document_description)}. {capitalize(document.document_summary)}.
          </p>
        ) : null}
      </div>
      {["image"].includes(document.type) && document.files?.[0] ? (
        <DocumentPreviewImage imageSrc={document.files[0].upload_url} />
      ) : null}
      {["audio"].includes(document.type) && document.files?.[0] ? (
        <DocumentPreviewAudio src={document.files[0].upload_url} controls />
      ) : null}
      {["video"].includes(document.type) && document.files?.[0] ? (
        <ReactPlayer width="120px" height="" url={document.files[0].upload_url} controls={false} />
      ) : null}
    </div>
  );
};

export const DiscoveryBox = () => {
  const matches = useMatch("/case/:caseId/*");
  const caseId = Number(matches?.params?.caseId);
  const { data: documents = [] } = useDocuments(caseId);
  const [lastUploadedFileAt, setLastUploadedFileAt] = useState<Date>();
  const [isAddingFile, setIsAddingFile] = useState(false);
  // @ts-ignore
  const onSubmitFile = (type: "audio" | "image" | "pdf" | "video") => (e) => {
    e.preventDefault();
    if (e.target.file?.files?.[0]) {
      // --- setup form data/submit
      const formData = new FormData();
      formData.append("file", e.target.file.files[0]);
      axios.post(`${getGideonApiUrl()}/v1/documents/index/${type}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        params: { case_id: caseId },
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
          <li key={doc.id}>
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

          {/* VIDEO */}
          <form className="discovery-box__file-uploader" onSubmit={onSubmitFile("video")}>
            <input type="file" name="file" accept=".mp4,.mov" />
            <button type="submit">Upload Video</button>
          </form>
        </>
      ) : (
        <button className="add-files-btn" onClick={() => setIsAddingFile(true)}>
          + Upload PDF, Image, Audio, Video
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
    display: flex;
    justify-content: space-between;
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
