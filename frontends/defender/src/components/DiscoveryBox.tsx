import axios from "axios";
import { capitalize } from "lodash";
import React, { useEffect, useState } from "react";
import ReactPlayer from "react-player";
import { Link } from "react-router-dom";
import styled from "styled-components";
import { useAppStore } from "../data/AppStore";
import { reqIndexDocument } from "../data/reqIndexDocument";
import { TDocument, useDocuments } from "../data/useDocuments";
import { getGideonApiUrl } from "../env";
import { formatSecondToTime } from "./formatSecondToTime";

const DocumentPreviewMedia = styled.div`
  min-width: 120px;
  max-width: 120px;
  width: 120px;
  display: flex;
  align-items: center;
`;
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
  const { focusedCaseId } = useAppStore();
  const pageCount = Math.max(...Array.from(new Set(document?.content?.map((dc) => Number(dc.page_number)))));
  const timeText = formatSecondToTime(
    Math.max(...Array.from(new Set(document?.content?.map((dc) => Number(dc.second_end)))))
  );
  return (
    <div className="discovery-box__document">
      <div style={{ flexGrow: 1 }}>
        <small>
          <Link to={`/case/${focusedCaseId}/document/${document.id}`}>{document.name ?? "n/a"}</Link>
          {["audio", "video"].includes(document?.type) ? <> ({timeText} min.)</> : null}
          {document?.type === "pdf" ? <> ({pageCount} pages)</> : null}
        </small>
        {["audio", "docx", "pdf", "video"].includes(document.type) ? (
          <>
            <p>{document.generated_description}</p>
            <div className="discovery-box__document__actions">
              <div>
                <small>{document.generated_summary_one_liner}</small>
              </div>
            </div>
          </>
        ) : null}
        {["image"].includes(document.type) ? (
          <p>
            {capitalize(document.generated_description)}. {capitalize(document.generated_summary)}.
          </p>
        ) : null}
      </div>
      {["image"].includes(document.type) && document.files?.[0] ? (
        <DocumentPreviewImage imageSrc={document.files[0].upload_url} />
      ) : null}
      {["audio"].includes(document.type) && document.files?.[0] ? (
        <DocumentPreviewMedia>
          <DocumentPreviewAudio src={document.files[0].upload_url} controls />
        </DocumentPreviewMedia>
      ) : null}
      {["video"].includes(document.type) && document.files?.[0] ? (
        <DocumentPreviewMedia>
          <ReactPlayer
            width="120px"
            height=""
            url={document?.files?.find((f) => f.mime_type?.includes("video"))?.upload_url}
            controls={false}
          />
        </DocumentPreviewMedia>
      ) : null}
    </div>
  );
};

export const DiscoveryBox: React.FC<{ caseId: number }> = ({ caseId }) => {
  const { data: documents, refetch } = useDocuments({ caseId });

  // @ts-ignore
  const onSubmitFile = (e) => {
    e.preventDefault();
    // @ts-ignore
    reqIndexDocument(e.target?.file?.files ?? [], { caseId }).then(() => {
      setTimeout(() => refetch(), 1000 * 2);
    });
    // --- clear file in input if successful
    e.target.file.value = "";
  };

  // RENDER
  return (
    <>
      <StyledDiscoveryBoxLead>
        <h2>Discovery</h2>
        <form className="discovery-box__file-uploader" onSubmit={(e) => onSubmitFile(e)}>
          <input type="file" name="file" accept=".pdf,.jpg,.jpeg,.png,.m4a,.mp3,.mp4,.mov,.docx" />
          <button type="submit">+ Upload</button>
        </form>
      </StyledDiscoveryBoxLead>
      <StyledDiscoveryBox>
        {!caseId ? null : (
          <>
            {/* DOCUMENTS - PROCESSING */}
            {documents
              ?.filter((d) => d.status_processing_content != "completed")
              .map((d) => (
                <div key={d.id} className="discovery-box__document processing">
                  <p>
                    File "<Link to={`/case/${caseId}/document/${d.id}`}>{d.name}</Link>" processing...
                  </p>
                </div>
              ))}
            {/* DOCUMENTS - PROCESSED */}
            <ul>
              {documents
                ?.filter((d) => d.status_processing_content === "completed")
                .map((doc) => (
                  <li key={doc.id}>
                    <DocumentBox document={doc} />
                  </li>
                ))}
            </ul>
          </>
        )}
      </StyledDiscoveryBox>
    </>
  );
};

const StyledDiscoveryBoxLead = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 4px;
  h2 {
    font-size: 18px;
    font-weight: 900;
  }
  form {
    display: flex;
    justify-content: flex-end;
    align-items: center;
  }
  .discovery-box__file-uploader {
    input {
      max-width: 180px;
    }
  }
`;

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
    border: 1px solid #eee;
    &:hover {
      border: 1px solid blue;
    }
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
    padding-top: 4px;
    margin-top: 6px;
    small {
      cursor: pointer;
    }
  }
`;
