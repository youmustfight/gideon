import axios from "axios";
import React, { useState } from "react";
import styled from "styled-components";
import { getGideonApiUrl } from "../env";

export const CAPCaseLawDriver: React.FC = () => {
  const [caseNumber, setCaseNumber] = useState("");
  const indexCAPCaseLaw = async () => {
    return axios
      .post(`${getGideonApiUrl()}/v1/cap/caselaw/index`, {
        cap_ids: [Number(caseNumber)],
      })
      .then(() => setCaseNumber(""));
  };
  // RENDER
  return (
    <StyledCAPCaseLawDriver>
      <div>
        <label htmlFor="case-selector">Index CAP Caselaw ID</label>
        <input id="case-selector" value={caseNumber} onChange={(e) => setCaseNumber(e.target.value)} />
        <button onClick={() => indexCAPCaseLaw()}>+ Index Case</button>
      </div>
    </StyledCAPCaseLawDriver>
  );
};

const StyledCAPCaseLawDriver = styled.div`
  // background: white;
  // border-radius: 4px;
  margin: 12px 0;
  // padding: 12px;
  select {
    width: 100%;
  }
  & > div {
    display: flex;
    align-items: center;
    button {
      margin: 0 4px;
      white-space: pre;
    }
    label {
      margin-right: 8px;
      font-size: 13px;
      width: 80px;
      min-width: 80px;
      max-width: 80px;
    }
    input,
    select {
      width: 100%;
    }
  }
`;
