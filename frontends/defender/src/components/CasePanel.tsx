import React from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { useAIRequestStore } from "./AIRequest/AIRequestStore";
import { TCase } from "../data/useCase";
import { BoxWithRightSideButton } from "./styled/StyledBox";

export const CasePanel: React.FC<{ cse: TCase }> = ({ cse }) => {
  const navigate = useNavigate();
  const { setInquiryScope, inquiry } = useAIRequestStore();

  return (
    <StyledCasePanel key={cse.id}>
      <span>
        {cse.name ?? "Untitled Case"}
        <small className="case-panel__users">
          <span className="case-panel__users__assigned">👩‍💼:</span> {cse.users?.map((u) => u.name).join(", ")}
        </small>
      </span>
      <div className="case-panel__actions">
        <button
          className="view-cases-like-this-btn"
          onClick={() => {
            setInquiryScope("organization");
            inquiry({ caseId: cse.id, organizationId: cse.organization_id });
          }}
        >
          View Cases Like This
        </button>
        &ensp;
        <button onClick={() => navigate(`/case/${cse.id}`)}>➡</button>
      </div>
    </StyledCasePanel>
  );
};

const StyledCasePanel = styled(BoxWithRightSideButton)`
  display: flex;
  justify-content: space-between;
  .case-panel__users {
    display: block;
    margin-top: 4px;
    font-size: 12px;
  }
  .case-panel__actions {
    text-align: right;
  }
  .view-cases-like-this-btn {
    display: none;
  }
  &:hover {
    .view-cases-like-this-btn {
      display: initial;
    }
  }
`;
