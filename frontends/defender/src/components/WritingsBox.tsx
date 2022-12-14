import React from "react";
import { Link, useMatch } from "react-router-dom";
import styled from "styled-components";
import { useWritingCreate } from "../data/useWritingCreate";
import { useWritings } from "../data/useWritings";

export const WritingsBox = () => {
  const matches = useMatch("/case/:caseId/*");
  const caseId = Number(matches?.params?.caseId);
  const { data: writings } = useWritings(caseId);
  const { mutateAsync: writingCreate } = useWritingCreate();

  return (
    <StyledWritingsBox>
      <button className="add-files-btn" onClick={() => writingCreate({ caseId })}>
        + Create New Writing
      </button>
      {writings?.map((w) => (
        <div key={w.id} className="writings-box__writing">
          <p>
            <Link to={`/case/${caseId}/writing/${w.id}`}>{w.name ?? "Untitled"}</Link>
          </p>
        </div>
      ))}
    </StyledWritingsBox>
  );
};

const StyledWritingsBox = styled.div`
  button {
    width: 100%;
  }
  .writings-box__writing {
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
`;
