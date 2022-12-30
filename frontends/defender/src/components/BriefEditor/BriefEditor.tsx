import { cloneDeep } from "lodash";
import React, { useState } from "react";
import { useDebounce } from "react-use";
import styled from "styled-components";
import { TBrief, TBriefFact, TBriefIssue, useBrief, useBriefCreate, useBriefUpdate } from "../../data/useBrief";
import { useCase } from "../../data/useCase";
import { BriefEditorFact } from "./BriefEditorFact";
import { BriefEditorIssue } from "./BriefEditorIssue";

type TBriefEditorUpdaterProps = {
  brief: TBrief;
  caseId: number;
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
      <hr />
      {/* ISSUES */}
      <StyledBriefBoxLead>
        <h3>Issues</h3>
        <button onClick={() => updateBriefAddIssue()}>+ Issue</button>
      </StyledBriefBoxLead>
      <StyledBriefBox>
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
      </StyledBriefBox>
      <hr />
      {/* FACTS */}
      <StyledBriefBoxLead>
        <h3>Relevant Facts</h3>
        <button onClick={() => updateBriefAddFact()}>+ Fact</button>
      </StyledBriefBoxLead>
      <StyledBriefBox>
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
      </StyledBriefBox>
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
  // SETUP
  const { data: cse } = useCase(caseId);
  const { data: brief } = useBrief({ caseId });
  const [initialIssues, setInitialIssues] = useState<TBriefIssue[]>([]);
  const [wantsToCreateNewBrief, setWantsToCreateNewBrief] = useState(false);
  // --- generate brief
  const { mutateAsync: briefCreate, isIdle: isIdleBriefCreate } = useBriefCreate();
  // --- editor state

  // RENDER
  return (
    <>
      <StyledBriefBoxLead>
        <h2>"{cse?.name ?? "Untitled"}" Case Brief</h2>
        {brief && !wantsToCreateNewBrief && (
          <button
            onClick={() => {
              setInitialIssues(brief?.issues ?? []);
              setWantsToCreateNewBrief(true);
            }}
          >
            + Generate New Brief
          </button>
        )}
        {brief && wantsToCreateNewBrief ? (
          <button onClick={() => setWantsToCreateNewBrief(false)}>← Back to Current Brief</button>
        ) : null}
      </StyledBriefBoxLead>
      {!brief || wantsToCreateNewBrief ? (
        <>
          <hr />
          <StyledBriefBoxLead>
            <h3>Issues</h3>
            <button onClick={() => setInitialIssues(initialIssues.concat({ issue: "" }))}>+ Issue</button>
          </StyledBriefBoxLead>
          <StyledBriefBox>
            {initialIssues.map((issue, issueIndex, issuesArr) => (
              <div key={issueIndex} className="issue-row">
                <label>
                  <span>Issue #{issueIndex + 1}:</span>
                  <input
                    value={issue.issue}
                    placeholder="Whether..."
                    onChange={(e) => {
                      const updatedIssues = cloneDeep(issuesArr);
                      updatedIssues[issueIndex] = { issue: e.target.value };
                      setInitialIssues(updatedIssues);
                    }}
                  />
                  <button
                    onClick={() =>
                      setInitialIssues(issuesArr.slice(0, issueIndex).concat(issuesArr.slice(issueIndex + 1)))
                    }
                  >
                    Remove
                  </button>
                </label>
              </div>
            ))}
            <br />
            <button
              style={{ width: "100%" }}
              disabled={initialIssues.length === 0 || !isIdleBriefCreate}
              onClick={() => briefCreate({ caseId, issues: initialIssues })}
            >
              {isIdleBriefCreate ? "Generate Case Brief with AI" : "Generating case brief..."}
            </button>
          </StyledBriefBox>
        </>
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
  margin-bottom: 4px;
  padding: 4px;
  h2 {
    font-size: 20px;
    font-weight: 900;
    text-decoration: underline;
  }
  h3 {
    font-size: 16px;
    font-weight: 900;
    text-decoration: underline;
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
    & > li {
      margin-bottom: 5px !important;
    }
  }
`;
