import React from "react";
import { Route, Routes } from "react-router";
import styled from "styled-components";
import { QuestionAnswerBox } from "./components/QuestionAnswerBox";
import { GideonCaseView } from "./GideonCaseView";
import { GideonDocumentView } from "./GideonDocumentView";

export const Gideon: React.FC = () => {
  // RENDER
  return (
    <StyledGideon>
      <div style={{ width: "100%", background: "gray", textAlign: "center", padding: "4px" }}>
        TODO: multi-player case bar
      </div>

      <section>
        <QuestionAnswerBox />
      </section>

      <hr />

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
  .section-lead {
    width: 100%;
    text-align: center;
    margin: 4px 0;
    margin-top: 32px;
    h3,
    h4 {
      font-weight: 900;
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
  }
  .section-people {
    span.person-pill {
      margin: 0 6px 0 0;
    }
  }
`;
