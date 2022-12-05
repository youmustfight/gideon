import axios from "axios";
import React from "react";
import { Routes, Route, Navigate } from "react-router";
import { useMatch } from "react-router-dom";
import styled from "styled-components";
import { CaseDriver } from "../../components/CaseDriver";
import { QuestionAnswerBox } from "../../components/QuestionAnswerBox";
import { useCase } from "../../data/useCase";
import { ViewCaseDocument } from "./ViewCaseDocument";
import { ViewCaseOverview } from "./ViewCaseOverview";

export const ViewCase = () => {
  const matches = useMatch("/case/:caseId/*");
  const caseId = Number(matches?.params?.caseId);
  const { data: cse } = useCase(caseId);

  // RENDER
  return (
    <>
      <CaseDriver />
      <StyledViewCase>
        {/* --- AI inputs --- */}
        <section>
          <QuestionAnswerBox />
        </section>

        {/* --- CASE VIEWS ---  */}
        <Routes>
          {/* --- document inspection */}
          <Route path="/:caseId/document/:documentId" element={<ViewCaseDocument />} />
          {/* --- overview */}
          <Route path="/:caseId/" element={<ViewCaseOverview />} />
          {/* --- default overview showing. TODO: figure out relative path version */}
          {/* <Route path="/*" element={<Navigate to={`/case/${caseId}/overview`} />} /> */}
        </Routes>

        {/* --- ADMIN ---  */}
        <hr />
        <br />
        <div className="section-lead">
          <h4>ADMIN</h4>
        </div>
        <section className="section-admin">
          <button onClick={() => axios.put(`/v1/case/${caseId}/ai_action_locks_reset`)}>Reset AI Action Locks</button>
        </section>
      </StyledViewCase>
    </>
  );
};

const StyledViewCase = styled.div`
  a,
  a:active a:visited,
  a:hover {
    color: blue !important;
    text-decoration: none;
  }
  a:hover {
    text-decoration: underline;
  }
  .section-lead {
    display: flex;
    flex-direction: column;
    text-align: left;
    padding: 0 16px;
    margin: 4px 20px;
    h2 {
      font-size: 20px;
      font-weight: 900;
      margin: 6px 0;
    }
    h3,
    h4 {
      font-weight: 900;
      margin: 6px 0;
      display: flex;
    }
  }
  section {
    box-shadow: rgb(0 0 0 / 4%) 0px 0 60px 0px;
    border-radius: 24px;
    padding: 12px;
    margin: 10px 24px;
    &:first-of-type {
      margin-top: 0;
      box-shadow: none;
    }
    &:last-of-type {
      margin-bottom: 0;
    }
    ul {
      list-style-type: disc;
      padding-left: 12px;
      li {
        font-size: 13px;
        margin: 3px 0;
      }
    }
    &.no-shadow {
      box-shadow: none;
    }
  }
  .section-people {
    span.person-pill {
      margin: 0 6px 0 0;
    }
  }
  .section-admin {
    padding: 1em;
    display: flex;
    text-align: center;
    flex-direction: column;
  }
`;
