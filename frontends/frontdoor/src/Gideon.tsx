import React from "react";
import styled from "styled-components";

export const Gideon: React.FC = () => {
  // RENDER
  return (
    <StyledGideon>
      <div className="intro-box">
        <h1>Gideon</h1>
        <small>Legal Assistance for All</small>
      </div>
      <div className="button-box">
        <a href="https://defender.gideon.foundation" target="_blank" rel="noreferer noopener">
          <button>Document Assistant Tool for Nashua, New Hampshire Public Defenders (MVP)</button>
        </a>
        +
        <br />
        <a
          href="https://docs.google.com/spreadsheets/d/1WLqK9HIzQvvuz7Tq_TtEkI85PEwsQhWnnnQF4ZbOl0Q"
          target="_blank"
          rel="noreferer noopener"
        >
          <button>Caselaw Summaries for Citing Slavery, Harvard Caselaw Access Project (Proof of Concept)</button>
        </a>
        =
        <br />
        <button disabled>Co-Pilot Litigation & Motion Writing (Future)</button>
      </div>
    </StyledGideon>
  );
};

const StyledGideon = styled.main`
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  & > div {
    max-width: 100%;
  }
  .intro-box {
    margin: 1em;
    text-align: center;
    h1 {
      font-size: 26px;
      margin-bottom: 8px;
    }
  }
  .button-box {
    display: flex;
    flex-direction: column;
    margin: 1em;
    text-align: center;
    button {
      margin: 8px 0;
      width: 100%;
    }
  }
`;
