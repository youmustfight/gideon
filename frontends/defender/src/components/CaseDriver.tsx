import React from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { useCase, useCaseUpdate } from "../data/useCase";

export const CaseDriver: React.FC<{ caseId: number }> = ({ caseId }) => {
  const navigate = useNavigate();
  const { data: cse } = useCase(caseId);
  const { mutateAsync: caseUpdate } = useCaseUpdate();

  // RENDER
  return !cse ? null : (
    <StyledCaseDriver isViewingCase={cse != null}>
      <div>
        <button onClick={() => navigate("/cases")}>⬅</button>
        {/* <label htmlFor="case-selector">Cases</label> */}
        <input value={cse.name} onChange={(e) => caseUpdate({ id: cse.id, name: e.target.value })} />
      </div>
    </StyledCaseDriver>
  );
};

const StyledCaseDriver = styled.div<{ isViewingCase: boolean }>`
  background: white;
  border-radius: 4px;
  margin: 12px;
  // margin-top: ${({ isViewingCase }) => (isViewingCase ? "0" : "24px")};
  padding: 12px;
  select {
    width: 100%;
  }
  & > div {
    display: flex;
    align-items: center;
    button {
      margin: 0 4px;
      white-space: pre;
    }
    label {
      margin-right: 8px;
      font-size: 13px;
      width: 80px;
      min-width: 80px;
      max-width: 80px;
    }
    input,
    select {
      width: 100%;
    }
  }
`;
