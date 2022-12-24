import React from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { TCase } from "../data/useCase";
import { BoxWithRightSideButton } from "./styled/StyledBox";

export const CasePanel: React.FC<{ cse: TCase }> = ({ cse }) => {
  const navigate = useNavigate();
  return (
    <StyledCasePanel key={cse.id}>
      <span>
        {cse.name ?? "Untitled Case"}
        <small className="case-panel__users">
          <span className="case-panel__users__assigned">👩‍💼:</span> {cse.users?.map((u) => u.name).join(", ")}
        </small>
      </span>
      <div>
        {/* <button onClick={() => viewSimilarCasesHandler(c.id)}>View Cases Like This</button>
        &ensp; */}
        <button onClick={() => navigate(`/case/${cse.id}`)}>➡</button>
      </div>
    </StyledCasePanel>
  );
};

const StyledCasePanel = styled(BoxWithRightSideButton)`
  .case-panel__users {
    display: block;
    margin-top: 4px;
    font-size: 12px;
  }
`;
