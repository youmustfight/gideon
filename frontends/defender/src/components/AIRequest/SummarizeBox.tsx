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
    summaryInput,
    setSummaryInput,
    summarize,
  } = useAIRequestStore();

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
            disabled={
              isAIRequestSubmitted ||
              !(summaryInput?.text.length > 400 || summaryInput?.issues?.length > 0 || params?.documentId != null)
            }
            onClick={() => summarize({ caseId: params?.caseId, documentId: params?.documentId })}
          >
            Run AI
          </button>
        </div>
        <div className="ai-request-box__input__row">
          {summaryScope === "text" ? (
            <textarea
              disabled={isAIRequestSubmitted}
              placeholder="Paste a very long text document..."
              value={summaryInput.text}
              rows={5}
              onChange={(e) => setSummaryInput({ text: e.target.value })}
            />
          ) : null}
          {summaryScope === "case" && params?.caseId != null ? <BriefAIGenerator /> : null}
        </div>
      </div>

      {isAIRequestSubmitted && (
        <>
          {/* TABS */}
          <div className="ai-request-box__tabs">
            <label className="active">
              {(() => {
                if (summaryScope === "text") return "Summary";
                if (summaryScope === "case") return "Case Brief";
                if (summaryScope === "document") return "Document Summary";
              })()}{" "}
              {answerSummary?.inProgress ? "(Processing...)" : ""}
            </label>
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

export const BriefAIGenerator: React.FC = () => {
  const { isAIRequestSubmitted, summaryInput, setSummaryInput } = useAIRequestStore();
  // RENDER
  return (
    <StyledBriefAIGenerator>
      <div className="brief-editor-gen__instructions">
        <p>Use AI to generate a case brief. To start, list case issues below. Click 'Run AI' when done.</p>
      </div>
      <div className="brief-editor-gen__row">
        <h3>Issues</h3>
        <button
          disabled={isAIRequestSubmitted}
          onClick={() =>
            setSummaryInput({
              ...summaryInput,
              issues: (summaryInput?.issues ?? []).concat({ issue: "" }),
            })
          }
        >
          + Issue
        </button>
      </div>
      <div>
        {summaryInput?.issues?.map((issue, issueIndex, issuesArr) => (
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
                  setSummaryInput({ ...summaryInput, issues: updatedIssues });
                }}
              />
              <button
                disabled={isAIRequestSubmitted}
                onClick={() => {
                  setSummaryInput({
                    ...summaryInput,
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
    </StyledBriefAIGenerator>
  );
};

const StyledBriefAIGenerator = styled.div`
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
