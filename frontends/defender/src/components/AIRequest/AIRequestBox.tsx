import React, { useEffect, useState } from "react";
import styled from "styled-components";
import { TAIRequestType, useAIRequestStore } from "./AIRequestStore";
import { InquiryBox } from "./InquiryBox";
import { SummarizeBox } from "./SummarizeBox";
import { WriteBox } from "./WriteBox";

export const AIRequestTypeSelect = ({ disabled }: { disabled: boolean }) => {
  const { aiRequestType, setAIRequestType } = useAIRequestStore();
  return (
    <select
      value={aiRequestType}
      disabled={disabled}
      onChange={(e) => setAIRequestType(e.target.value as TAIRequestType)}
      style={{ maxWidth: "90px" }}
    >
      <option value="inquiry">Ask</option>
      <option value="summarize">Summarize</option>
      <option value="write">Write</option>
    </select>
  );
};

export const AIRequestBox = () => {
  const { aiRequestType, clearAIRequest, setAIRequestType } = useAIRequestStore();
  // MOUNT
  useEffect(() => {
    // TODO: maybe don't do this so we don't lose search answers as we move between sections?
    // --- reset focus of request box to inquiry since that'll be most common?
    setAIRequestType("inquiry");
    clearAIRequest();
  }, []);

  // RENDER
  return (
    <StyledAIRequestBox>
      {/* REQUEST INTERFACES */}
      {aiRequestType === "inquiry" ? <InquiryBox /> : null}
      {aiRequestType === "summarize" ? <SummarizeBox /> : null}
      {aiRequestType === "write" ? <WriteBox /> : null}
    </StyledAIRequestBox>
  );
};

const StyledAIRequestBox = styled.div`
  display: flex;
  margin: -6px 12px 0 !important;
  background: white;
  padding: 12px;
  padding-top: 12px !important;
  margin-bottom: 12px;
  & > select {
    font-size: 13px;
  }
  div {
    flex-grow: 1;
  }

  .ai-request-box__input {
    display: flex;
    width: 100%;
    justify-content: space-between;
    label,
    input,
    select {
      width: 100%;
      display: flex;
      flex-grow: 1;
      align-items: center;
    }
    label > span {
      min-width: 120px;
      font-size: 12px;
    }
    select {
      max-width: 100px;
    }
    button[type="submit"] {
      font-size: 12px;
      max-width: 80px;
      width: 100%;
    }
    &.rows {
      flex-direction: column;
    }
  }
  .ai-request-box__input__row {
    display: flex;
    width: 100%;
    justify-content: space-between;
    & > * {
      flex-grow: 1;
    }
  }

  .ai-request-box__tabs {
    padding: 4px 0;
    margin-top: 12px;
    display: flex;
    label {
      display: flex;
      align-items: center;
      justify-content: center;
      flex: 1;
      flex-grow: 1;
      text-align: center;
      padding: 4px 0;
      margin: 0 2px;
      border-bottom: 2px solid #eee;
      color: #aaa;
      cursor: pointer;
      font-size: 14px;
      background: #eee;
      &.active {
        border-bottom: 2px solid blue;
        background: blue;
        color: white;
      }
    }
  }

  .ai-request-box__reset-inquiry-btn {
    width: 54px;
    max-width: 54px;
  }

  .ai-request-box__focus {
    padding-top: 12px;
    font-size: 13px;
    ul {
      list-style-type: none;
      padding-left: 0;
    }
    li {
      margin-top: 4px;
    }
    b {
      font-weight: 700;
    }
  }
`;
