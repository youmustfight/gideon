import React, { useState } from "react";
import styled from "styled-components";
import { reqCaseAILocksReset, reqCaseReindexAllDocuments } from "../data/useCase";

export const CaseAdminToolbox: React.FC<{ caseId: number }> = ({ caseId }) => {
  const [isVisible, setIsVisible] = useState(false);
  // RENDER
  return !caseId ? null : (
    <StyledCaseAdminToolbox>
      <u onClick={() => setIsVisible(!isVisible)}>
        <small>Show/Hide Admin Tools</small>
      </u>
      {isVisible ? (
        <div>
          <button onClick={() => reqCaseAILocksReset(caseId)}>Reset AI Action Locks</button>
          <button onClick={() => reqCaseReindexAllDocuments(caseId)}>Re-Index All Documents</button>
        </div>
      ) : null}
    </StyledCaseAdminToolbox>
  );
};

const StyledCaseAdminToolbox = styled.div`
  small,
  button {
    font-size: 12px;
  }
  div {
    display: flex;
    flex-direction: column;
    margin-top: 4px;
  }
`;
