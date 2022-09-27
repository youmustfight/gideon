import { flatten } from "lodash";
import React, { useState } from "react";
import styled from "styled-components";
import { DiscoveryBox } from "./components/DiscoveryBox";
import { QuestionAnswerBox } from "./components/QuestionAnswerBox";
import { useDocuments } from "./data/useDocuments";

export const Gideon: React.FC = () => {
  const { data: documents = [] } = useDocuments();
  const [selectedPerson, setSelectedPerson] = useState();
  const [selectedDoc, setSelectedDoc] = useState<string>();

  // RENDER
  return (
    <StyledGideon>
      <section>
        <QuestionAnswerBox />
      </section>

      {/* DISCOVERY/INDEXED DOCS + UPLOAD */}
      <div className="section-lead">
        <h4>Discovery, Evidence, Exhibits</h4>
      </div>
      <section>
        <DiscoveryBox documents={documents} />
      </section>

      {/* PEOPLE */}
      <div className="section-lead">
        <h4>People</h4>
      </div>
      <section className="section-people">
        {flatten(documents.map((f) => Object.keys(f.people ?? {}))).map((p) => (
          <span key={p} className="person-pill" onClick={() => setSelectedPerson(selectedPerson === p ? null : p)}>
            {p}
          </span>
        ))}
      </section>

      {/* TIMELINE */}
      <div className="section-lead">
        <h4>Events, Timelines</h4>
      </div>
      <section>
        <div>
          <ul>
            {flatten(documents.map((f) => f.event_timeline ?? [])).map((str) => (
              <li key={str}>{str}</li>
            ))}
          </ul>
        </div>
      </section>
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
