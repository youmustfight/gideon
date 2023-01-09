import { Link } from "react-router-dom";
import styled from "styled-components";
import { TQueryLocation } from "./AIRequest/aiRequestReqs";
import { formatSecondToTime } from "./formatSecondToTime";
import { formatHashForSentenceHighlight } from "./hashUtils";

export const DocumentContentLocationBox = ({ location }: { location: TQueryLocation }) => {
  return (
    <StyledDocumentContentLocationBox>
      {location.document && (
        <div className="answer-location-box__text">
          <b>
            <Link to={`/case/${location.case_id}/document/${location.document.id}`}>
              {location.document.name ?? "n/a"}
            </Link>
            <span>
              {location.document.type === "pdf" ? (
                <>
                  <Link
                    to={`/case/${location.case_id}/document/${location.document.id}#${formatHashForSentenceHighlight(
                      location.document_content.sentence_number ?? location.document_content.sentence_start,
                      location.document_content.sentence_end
                    )}`}
                  >
                    {location.document_content.page_number
                      ? `page ${location.document_content.page_number}`
                      : `${formatHashForSentenceHighlight(
                          location.document_content.sentence_number ?? location.document_content.sentence_start,
                          location.document_content.sentence_end
                        )}`}
                  </Link>
                </>
              ) : null}
              {["audio", "video"].includes(location.document.type) ? (
                <>
                  <Link
                    to={`/case/${location.case_id}/document/${location.document.id}#${formatHashForSentenceHighlight(
                      location.document_content.sentence_number ?? location.document_content.sentence_start,
                      location.document_content.sentence_end
                    )}`}
                  >
                    {formatSecondToTime(location.document_content.second_start ?? 0)}
                  </Link>
                </>
              ) : null}
            </span>
          </b>
          {location.document_content.text && location.document_content.tokenizing_strategy === "sentence" ? (
            <p>"...{location.document_content.text}..."</p>
          ) : null}
        </div>
      )}
      {location.image_file ? <StyledDocumentContentLocationBoxImage imageSrc={location.image_file.upload_url} /> : null}
    </StyledDocumentContentLocationBox>
  );
};

const StyledDocumentContentLocationBox = styled.div`
  margin-top: 4px;
  min-height: 20px;
  font-size: 12px;
  display: flex;
  align-items: center;
  background: white;
  padding: 8px;
  border-radius: 6px;
  & > div.answer-location-box__text {
    flex-grow: 1;
    b {
      font-size: 12px;
      display: flex;
      justify-content: space-between;
    }
    p {
      margin: 8px 0 0;
    }
  }
`;

const StyledDocumentContentLocationBoxImage = styled.div<{ imageSrc: string }>`
  width: 100%;
  max-width: 120px;
  min-height: 60px;
  max-height: 60px;
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  background-image: url(${(props) => props.imageSrc});
  margin-left: 8px;
`;
