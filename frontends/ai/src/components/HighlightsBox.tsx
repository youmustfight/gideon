import axios from "axios";
import React, { useState } from "react";
import { Link } from "react-router-dom";
import styled from "styled-components";
import { TQueryLocation } from "../data/useDocuments";
import { TDocumentHighlight, useHighlights } from "../data/useHighlights";
import { AnswerLocationBox } from "./QuestionAnswerBox";

export const HighlightBox: React.FC = (props: { highlight: TDocumentHighlight }) => {
  // SETUP
  const hl = props.highlight;
  // --- request like this
  const [locations, setLocations] = useState<TQueryLocation[]>([]);
  const [isSearchPending, setIsSearchPending] = useState(false);
  const handleSearchLocationsLikeThis = () => {
    setIsSearchPending(true);
    return axios
      .post("http://localhost:3000/v1/queries/vector-info-locations", {
        vector: props.highlight.highlight_text_vector,
      })
      .then((res) => {
        setLocations(res.data.locations);
        setIsSearchPending(false);
      });
  };

  // RENDER
  return (
    <StyledHighlightBox>
      <div className="highlight__header">
        <small>
          <Link to={`/document/${hl.filename}#sentence-index-${hl.document_text_vectors_by_sentence_start_index}`}>
            {hl.filename}
          </Link>
        </small>
        <small>by: {hl.user}</small>
      </div>
      <div className="highlight__note">
        <p>{hl.note_text}</p>
      </div>
      <div className="highlight__highlight">
        <p>"...{hl.highlight_text}..."</p>
        {locations?.length > 0 ? (
          <>
            <hr />
            <ul>
              {locations.map((l, locationIndex) => (
                <li key={locationIndex} className="highlight__location">
                  <AnswerLocationBox location={l} />
                </li>
              ))}
            </ul>
          </>
        ) : (
          <button disabled={isSearchPending} onClick={handleSearchLocationsLikeThis}>
            Search for Text/Testimony/Evidence Like This
          </button>
        )}
      </div>
    </StyledHighlightBox>
  );
};

const StyledHighlightBox = styled.div`
  background: #ffffcf;
  border-radius: 4px;
  margin-bottom: 12px;
  .highlight__header {
    display: flex;
    justify-content: space-between;
    padding: 12px 12px 4px;
    font-size: 12px;
  }
  .highlight__note {
    padding: 4px 12px;
    font-size: 14px;
    font-weight: 900;
  }
  .highlight__highlight {
    padding: 12px;
    & > p {
      font-size: 10px;
      font-style: italic;
    }
    button {
      font-size: 10px;
      width: 100%;
      margin-top: 4px;
    }
    & > ul {
      padding-left: 0 !important;
      list-style-type: none !important;
      .highlight__location {
        background: white;
        border-radius: 2px;
        margin: 6px;
        padding: 8px 12px;
      }
    }
  }
`;

export const HighlightsBox: React.FC = ({ filename }: { filename?: string }) => {
  const { data } = useHighlights();
  const highlights = data?.filter((hl) => {
    if (filename) return hl.filename === filename;
    return true;
  });
  // RENDER
  return (
    <StyledHighlightsBox>
      {highlights?.map((hl, hlIndex) => (
        <HighlightBox key={hlIndex} highlight={hl} />
      ))}
    </StyledHighlightsBox>
  );
};

const StyledHighlightsBox = styled.div``;
