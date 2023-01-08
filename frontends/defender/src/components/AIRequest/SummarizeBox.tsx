import { ResetIcon } from "@radix-ui/react-icons";
import { cloneDeep } from "lodash";
import React, { useEffect, useState } from "react";
import { useParams } from "react-router";
import styled from "styled-components";
import { AIRequestTypeSelect } from "./AIRequestBox";
import { TSummaryScope, useAIRequestStore } from "./AIRequestStore";

export const SummarizeBox = () => {
  const params = useParams(); // TODO: get from props, not params
  const {
    answerSummary,
    clearInquiry,
    isAIRequestSubmitted,
    summaryScope,
    setSummaryScope,
    summaryBriefInput,
    summaryTextInput,
    setSummaryTextInput,
    summarize,
  } = useAIRequestStore();

  // ON MOUNT
  // --- set initial search scope depending on vars available
  useEffect(() => {
    if (params?.documentId != null) {
      setSummaryScope("document");
    } else if (params.caseId != null) {
      setSummaryScope("case");
    } else {
      setSummaryScope("text");
    }
  }, [params]);

  // RENDER
  return (
    <StyledSummaryBox>
      <div className="ai-request-box__input rows">
        {/* Doing this inline bc we don't want to take up width on responses */}
        <div className="ai-request-box__input__row" key={summaryScope}>
          <AIRequestTypeSelect disabled={isAIRequestSubmitted} />
          <select
            value={summaryScope}
            disabled={isAIRequestSubmitted}
            onChange={(e) => setSummaryScope(e.target.value as TSummaryScope)}
            style={{ width: "100%", maxWidth: "100%" }}
          >
            <option value="text">Text</option>
            <option value="case" disabled={params?.caseId == null}>
              Case
            </option>
            <option value="document" disabled={params?.documentId == null}>
              Document
            </option>
          </select>
          <button
            type="submit"
            disabled={isAIRequestSubmitted || !(summaryTextInput.length > 400 || summaryBriefInput?.issues?.length > 0)}
            onClick={() => summarize()}
          >
            Run AI
          </button>
        </div>
        <div className="ai-request-box__input__row">
          {summaryScope === "text" ? (
            <textarea
              disabled={isAIRequestSubmitted}
              placeholder="Paste a very long text document..."
              value={summaryTextInput}
              rows={5}
              onChange={(e) => setSummaryTextInput(e.target.value)}
            />
          ) : null}
          {summaryScope === "case" && params?.caseId != null ? (
            <BriefEditorGenerator caseId={Number(params.caseId)} />
          ) : null}
        </div>
      </div>

      {isAIRequestSubmitted && (
        <>
          {/* TABS */}
          <div className="ai-request-box__tabs">
            {summaryScope === "text" ? (
              <label className="active">Summary {answerSummary?.inProgress ? "(Processing...)" : ""}</label>
            ) : null}
            {summaryScope === "case" ? (
              <label className="active">Case Brief {answerSummary?.inProgress ? "(Processing...)" : ""}</label>
            ) : null}
            <label className="ai-request-box__reset-inquiry-btn" onClick={clearInquiry}>
              <ResetIcon />
            </label>
          </div>
          {/* FOCUS */}
          <div className="ai-request-box__focus">
            {answerSummary?.summary ? (
              <>
                <p>{answerSummary?.summary}</p>
              </>
            ) : null}
          </div>
        </>
      )}
    </StyledSummaryBox>
  );
};

const StyledSummaryBox = styled.div`
  display: flex;
  flex-direction: column;
  .ai-request-box__input {
    button,
    select {
      max-height: 22px;
    }
  }
`;

export const BriefEditorGenerator: React.FC<{ caseId: number }> = ({ caseId }) => {
  const { isAIRequestSubmitted, summaryBriefInput, setSummaryBriefInput } = useAIRequestStore();
  // ON MOUNT
  useEffect(() => {
    // --- ensure we've set the case id
    setSummaryBriefInput({ ...summaryBriefInput, caseId: caseId });
  }, []);

  // RENDER
  return (
    <StyledBriefEditorGenerator>
      <div className="brief-editor-gen__instructions">
        <p>Use AI to generate a case brief. To start, list case issues below. Click 'Run AI' when done.</p>
      </div>
      <div className="brief-editor-gen__row">
        <h3>Issues</h3>
        <button
          disabled={isAIRequestSubmitted}
          onClick={() =>
            setSummaryBriefInput({
              ...summaryBriefInput,
              issues: (summaryBriefInput?.issues ?? []).concat({ issue: "" }),
            })
          }
        >
          + Issue
        </button>
      </div>
      <div>
        {summaryBriefInput?.issues?.map((issue, issueIndex, issuesArr) => (
          <div key={issueIndex} className="brief-editor-gen__row">
            <label>
              <span>Issue #{issueIndex + 1}:</span>
              <input
                value={issue.issue}
                disabled={isAIRequestSubmitted}
                placeholder="Whether..."
                onChange={(e) => {
                  const updatedIssues = cloneDeep(issuesArr);
                  updatedIssues[issueIndex] = { issue: e.target.value };
                  setSummaryBriefInput({ ...summaryBriefInput, issues: updatedIssues });
                }}
              />
              <button
                disabled={isAIRequestSubmitted}
                onClick={() => {
                  setSummaryBriefInput({
                    ...summaryBriefInput,
                    issues: issuesArr.slice(0, issueIndex).concat(issuesArr.slice(issueIndex + 1)),
                  });
                }}
              >
                Remove
              </button>
            </label>
          </div>
        ))}
      </div>
    </StyledBriefEditorGenerator>
  );
};

const StyledBriefEditorGenerator = styled.div`
  .brief-editor-gen__instructions {
    text-align: center;
    box-sizing: border-box;
    background: #f5f5f5;
    font-size: 13px;
    padding: 6px;
    margin: 4px 0;
    font-style: italic;
  }
  .brief-editor-gen__row {
    display: flex;
    justify-content: space-between;
    margin-top: 4px;
    h3 {
      font-weight: 900;
    }
  }
`;
