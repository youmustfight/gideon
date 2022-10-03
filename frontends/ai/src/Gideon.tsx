import React from "react";
import { Route, Routes } from "react-router";
import styled from "styled-components";
import { QuestionAnswerBox } from "./components/QuestionAnswerBox";
import { TeamHeader } from "./components/TeamHeader";
import { GideonCaseView } from "./GideonCaseView";
import { GideonDocumentView } from "./GideonDocumentView";

export const Gideon: React.FC = () => {
  // RENDER
  return (
    <StyledGideon>
      {/* USERS */}
      <TeamHeader />

      {/* QUESTION BOX */}
      <section>
        <QuestionAnswerBox />
      </section>

      <hr />

      {/* CASE/DOCUMENT VIEWS */}
      <Routes>
        {/* Case View */}
        <Route path="/" element={<GideonCaseView />} />
        {/* Document View */}
        <Route path="/document/:filename" element={<GideonDocumentView />} />
      </Routes>
    </StyledGideon>
  );
};

const StyledGideon = styled.div`
  min-height: 100vh;
  background: #f1f4f8;
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
    text-align: left;
    padding: 0 16px;
    margin: 4px 20px;
    margin-top: 32px;
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
    padding: 16px;
    margin: 10px 20px;
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
  }
  .section-people {
    span.person-pill {
      margin: 0 6px 0 0;
    }
  }
`;
