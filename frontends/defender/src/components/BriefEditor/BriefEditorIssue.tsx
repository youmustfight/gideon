import { useState } from "react";
import styled from "styled-components";
import { TBriefIssue } from "../../data/useBrief";
import { ConfirmButton } from "../ConfirmButton";
import { Button } from "../styled/common/Button";
import { TextArea } from "../styled/common/Input";
import { SlimBox } from "../styled/StyledBox";

type TBriefEditorIssueProps = {
  briefIssue: TBriefIssue;
  caseId: number;
  onChange: (newIssueValue: TBriefIssue) => void;
  onDelete: (factToDelete: TBriefIssue) => void;
};

export const BriefEditorIssue: React.FC<TBriefEditorIssueProps> = ({ briefIssue, caseId, onChange, onDelete }) => {
  // SETUP
  const [isEditing, setIsEditing] = useState(briefIssue?.issue?.length === 0);
  const [issue, setIssue] = useState(briefIssue);
  // --- update handler
  const updateHandler = (updates: Partial<TBriefIssue>) => {
    const newIssue = { ...issue, ...updates };
    setIssue(newIssue);
    onChange(newIssue);
  };

  // RENDER
  return isEditing ? (
    <div>
      <StyledBriefIssueSlimBox>
        <TextArea value={issue.issue} rows={7} onChange={(e) => updateHandler({ issue: e.target.value })} />
        <div className="fact-edit__actions">
          <Button onClick={() => setIsEditing(false)}>Done</Button>
          <ConfirmButton prompts={["Delete", "Yes, Delete Issue"]} onClick={() => onDelete(briefIssue)} />
        </div>
      </StyledBriefIssueSlimBox>
    </div>
  ) : (
    <div>
      <p>
        <span>{briefIssue.issue}</span> <u onClick={() => setIsEditing(true)}>Edit</u>{" "}
      </p>
    </div>
  );
};

const StyledBriefIssueSlimBox = styled(SlimBox)`
  flex-direction: column;
  hr {
    width: 100%;
  }
  .fact-edit__actions {
    display: flex;
    justify-content: space-between;
    margin-top: 4px;
  }
  textarea {
    font-size: 13px !important;
  }
`;
