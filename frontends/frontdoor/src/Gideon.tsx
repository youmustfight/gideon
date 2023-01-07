import React from "react";
import styled from "styled-components";
// import Library1 from "./assets/library.jpg";

export const Gideon: React.FC = () => {
  // RENDER
  return (
    <Page>
      <StyledTop>
        <span>Gideon</span>
      </StyledTop>
      <StyledIntro>
        {/* <h1>Ensuring Legal Assistance for All</h1> */}
        <h1>Bringing the power of A.I. to those who protect us and our rights.</h1>
        <h2>
          Are you a public interest lawyer or impact litigator? →{" "}
          <a href="https://airtable.com/shrIqGlVPw2Qzsypn">Request Access to A.I. Tools & Assistance</a>
        </h2>
        {/* <div className="button-box">
          <a href="https://defender.gideon.foundation/login" target="_blank" rel="noreferer noopener">
            <button>Document Assistant Tool for Nashua, New Hampshire Public Defenders (MVP)</button>
          </a>
          +
          <br />
          <button disabled>Co-Pilot Litigation & Motion Writing (Future)</button>
          +
          <br />
          <a
            href="https://docs.google.com/spreadsheets/d/1WLqK9HIzQvvuz7Tq_TtEkI85PEwsQhWnnnQF4ZbOl0Q"
            target="_blank"
            rel="noreferer noopener"
          >
            <button>Caselaw Search & Understanding for Citing Slavery, Harvard CAP (Proof of Concept)</button>
          </a>
          =
          <br />
          <button disabled>AI Engine & Interface that Reflects Society's Codified Values</button>
        </div> */}
      </StyledIntro>
      <StyledFooter>
        <div>
          <small>
            Are you an engineer or researcher looking to align AI systems with the most vulnerabale?{" "}
            <a
              href="mailto:mark@gideon.foundation?subject=Interested in Gideon and AI Aligned with Human Rights"
              target="_blank"
            >
              Get in touch
            </a>
          </small>
        </div>
        <div>
          <small>
            Special thank you to attorneys at{" "}
            <a href="http://www.citingslavery.org/" target="_blank">
              Citing Slavery Project
            </a>
            ,{" "}
            <a href="http://www.refugeerights.org/" target="_blank">
              IRAP
            </a>
            , and{" "}
            <a href="https://www.weil.com/" target="_blank">
              Weil
            </a>{" "}
            for early feedback © 2022
          </small>
        </div>
      </StyledFooter>
    </Page>
  );
};

const Page = styled.div`
  min-height: 100vh;
  background: var(--color-bg);
  padding: 2em;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
`;

const StyledTop = styled.div`
  font-size: 24px;
  font-family: "GT Walsheim";
  font-weight: 700;
  letter-spacing: 0px;
  color: var(--color-font);
  text-transform: uppercase;
`;

const StyledIntro = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  flex-grow: 1;
  margin: 2em 0;
  h1 {
    font-size: 96px;
    font-family: "GT Walsheim";
    font-weight: 600;
    letter-spacing: -5px;
    line-height: 90%;
    color: var(--color-font);
    margin-bottom: 12px;
    @media (max-width: 45em) {
      font-size: 54px;
      letter-spacing: -1px;
      line-height: 95%;
    }
  }
  h2 {
    font-size: 22px;
    font-family: "GT Walsheim";
    font-weight: 300;
    color: var(--color-font);
    margin-left: 8px;
    line-height: 140%;
  }
  small {
    font-style: italic;
    font-size: 12px;
  }
`;

const StyledFooter = styled.div`
  margin-top: 1em;
  border-top: 2px dashed var(--color-font);
  padding: 0.5em 0;
  display: flex;
  justify-content: space-between;
  small {
    font-style: italic;
    font-size: 14px;
    color: var(--color-font);
  }
  & > div {
    margin-top: 4px;
  }
  @media (max-width: 45em) {
    flex-direction: column;
  }
`;
