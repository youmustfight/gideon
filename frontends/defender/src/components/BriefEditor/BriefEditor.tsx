import { cloneDeep } from "lodash";
import React, { useState } from "react";
import { ChevronDownIcon, ChevronUpIcon } from "@radix-ui/react-icons";
import { useDebounce } from "react-use";
import styled from "styled-components";
import { TBrief, TBriefFact, TBriefIssue, useBrief, useBriefCreate, useBriefUpdate } from "../../data/useBrief";
import { useCase } from "../../data/useCase";
import { useDocuments } from "../../data/useDocuments";
import { useAIRequestStore } from "../AIRequest/AIRequestStore";
import { BriefEditorFact } from "./BriefEditorFact";
import { BriefEditorIssue } from "./BriefEditorIssue";

type TBriefEditorUpdaterProps = {
  brief: TBrief;
  caseId: number;
};

const BriefBox: React.FC<{ children: React.ReactNode; isExpanded?: boolean; label: string }> = (props) => {
  const [isExpanded, setIsExpanded] = useState(props.isExpanded ?? false);
  return (
    <div>
      <StyledBriefBoxLead onClick={() => setIsExpanded(!isExpanded)}>
        <h3>{props.label}</h3>
        {isExpanded ? <ChevronUpIcon /> : <ChevronDownIcon />}
      </StyledBriefBoxLead>
      {isExpanded && <StyledBriefBox>{props.children}</StyledBriefBox>}
    </div>
  );
};

export const BriefEditorUpdater: React.FC<TBriefEditorUpdaterProps> = (props) => {
  // SETUP
  // --- create a clone so we can edit local state and send updates
  const [brief, setBrief] = useState(props.brief);
  const { mutateAsync: briefUpdate } = useBriefUpdate();
  // --- run updates w/ debouncer
  useDebounce(() => briefUpdate(brief), 1000 * 2, [brief]);
  // --- update issue handlers
  const updateBriefAddIssue = () => setBrief({ ...brief, issues: brief.issues.concat({ issue: "" }) });
  const updateBriefEditIssue = (index: number, value: TBriefIssue) => {
    const updatedIssues = cloneDeep(brief?.issues ?? []);
    updatedIssues[index] = value;
    setBrief({ ...brief, issues: updatedIssues });
  };
  const updateBriefDeleteIssue = (index: number) => {
    setBrief({ ...brief, issues: brief?.issues.slice(0, index).concat(brief?.issues.slice(index + 1)) });
  };
  // --- update fact handlers
  const updateBriefAddFact = () => setBrief({ ...brief, facts: brief.facts.concat({ text: "" }) });
  const updateBriefEditFact = (index: number, value: TBriefFact) => {
    const updatedFacts = cloneDeep(brief?.facts ?? []);
    updatedFacts[index] = value;
    setBrief({ ...brief, facts: updatedFacts });
  };
  const updateBriefDeleteFact = (index: number) => {
    setBrief({ ...brief, facts: brief?.facts.slice(0, index).concat(brief?.facts.slice(index + 1)) });
  };

  // RENDER
  return (
    <>
      {/* ISSUES */}
      <BriefBox label="Issues, Holding, Reason">
        <ul>
          {brief?.issues?.map((issue, issueIndex, issueAr) => (
            <li key={[issueAr.length, issueIndex].join("-")}>
              <BriefEditorIssue
                briefIssue={issue}
                caseId={brief.case_id}
                onChange={(newIssueValue) => updateBriefEditIssue(issueIndex, newIssueValue)}
                onDelete={() => updateBriefDeleteIssue(issueIndex)}
              />
            </li>
          ))}
        </ul>
        <u onClick={() => updateBriefAddIssue()}>+ Issue</u>
      </BriefBox>
      {/* FACTS */}
      <BriefBox label="Facts">
        <ul>
          {brief?.facts?.map((fact, factIndex, factArr) => (
            <li key={[factArr.length, factIndex].join("-")}>
              <BriefEditorFact
                briefFact={fact}
                caseId={brief.case_id}
                onChange={(newFactValue) => updateBriefEditFact(factIndex, newFactValue)}
                onDelete={() => updateBriefDeleteFact(factIndex)}
              />
            </li>
          ))}
        </ul>
        <button onClick={() => updateBriefAddFact()}>+ Fact</button>
      </BriefBox>
      {/* DEPRECATED EVENTS -- doesn't fit brief structure */}
      {/* <StyledBriefBoxLead>
            <h3>Events/Timeline</h3>
          </StyledBriefBoxLead>
          <StyledBriefBox style={{ margin: "0 4px" }}>
            <TimelineSummary caseId={caseId} />
          </StyledBriefBox> */}
    </>
  );
};

export const BriefEditor: React.FC<{ caseId: number }> = ({ caseId }) => {
  const { data: cse } = useCase(caseId);
  const { data: documents } = useDocuments({ caseId });
  const { data: brief } = useBrief({ caseId });
  const { mutateAsync: briefCreate, isIdle: isIdleBriefCreate } = useBriefCreate();
  const { scrollToAIRequestBox, setAIRequestType } = useAIRequestStore();

  // RENDER
  return (
    <>
      {/* <div>
        <h2 style={{ fontSize: "20px", paddingBottom: "12px", paddingTop: "12px" }}>
          "{cse?.name ?? "Untitled"}" Case Brief
        </h2>
      </div> */}
      {!brief ? (
        <div style={{ display: "flex", paddingTop: "8px", width: "100%" }}>
          <button
            disabled={!isIdleBriefCreate}
            onClick={() => briefCreate({ caseId: caseId, issues: [] })}
            style={{ flexGrow: "1" }}
          >
            + Create Blank Case Brief
          </button>
          <button
            onClick={() => {
              setAIRequestType("summarize");
              scrollToAIRequestBox();
            }}
            style={{ flexGrow: "1" }}
          >
            + Generate Case Brief with AI
          </button>
        </div>
      ) : (
        <BriefEditorUpdater brief={brief} caseId={caseId} />
      )}
    </>
  );
};

const StyledBriefBoxLead = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
  margin-bottom: 8px;
  padding: 6px;
  background: #f0f0f5;
  cursor: pointer;
  h2 {
    font-size: 16px;
    font-weight: 900;
  }
  h3 {
    font-size: 14px;
    font-weight: 900;
  }
`;

const StyledBriefBox = styled.div`
  margin-top: 4px;
  .issue-row {
    margin: 0 4px 4px;
    label {
      display: flex;
      span {
        width: 80px;
      }
      input {
        flex-grow: 1;
      }
    }
  }
  & > ul {
    margin-left: 12px;
    list-style-type: none;
    & > li {
      margin-bottom: 5px !important;
    }
  }
  & > button {
    margin: 4px auto;
    width: 100%;
  }
  & > u {
    margin-left: 24px;
    padding: 2px 0 6px;
    display: block;
    opacity: 0.5;
    &:hover {
      opacity: 1;
    }
  }
`;
