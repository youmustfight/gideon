import React from "react";
import { Link } from "react-router-dom";
import styled from "styled-components";
import { TCapCase } from "../data/useCapCase";

type TCapCasePanelProps = {
  capCase: TCapCase;
};

export const CapCasePanel: React.FC<TCapCasePanelProps> = ({ capCase }) => {
  // RENDER
  return (
    <StyledCapCasePanel>
      <div style={{ flexGrow: 1 }}>
        <div className="caselaw__header">
          <p>
            <Link to={`/caselaw/cap/${capCase.cap_id}`}>{capCase.name_abbreviation ?? "n/a"}</Link>
            <> ({capCase.decision_date.slice(0, 4)})</>
          </p>
        </div>
        <div className="caselaw__actions">
          <div>
            <small>
              {capCase.casebody.head_matter.slice(0, 280)}...{" "}
              <Link to={`/caselaw/cap/${capCase.cap_id}`}>Read More</Link>
            </small>
          </div>
        </div>
      </div>
    </StyledCapCasePanel>
  );
};

const StyledCapCasePanel = styled.div`
  background: white;
  border-radius: 4px;
  padding: 8px 12px 8px;
  margin: 4px 0;
  display: flex;
  justify-content: space-between;
  &.processing {
    opacity: 0.5;
    text-align: center;
    margin-bottom: 6px;
    margin-top: 0;
  }
  .caselaw__header {
    font-size: 13px;
  }
  .caselaw__expanded {
    border-top: 1px solid #eee;
    margin-top: 2px;
  }
  .caselaw__actions {
    border-top: 1px solid #eee;
    padding-top: 4px;
    margin-top: 6px;
    small {
      cursor: pointer;
    }
  }
`;
