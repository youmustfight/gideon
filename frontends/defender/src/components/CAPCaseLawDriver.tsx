import axios from "axios";
import React, { useState } from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { getGideonApiUrl } from "../env";
import { StyledDriverBox } from "./styled/StyledDriverBox";

export const CAPCaseLawDriver: React.FC = () => {
  const navigate = useNavigate();
  const [caseNumber, setCaseNumber] = useState("");
  const [showDetails, setShowDetails] = useState(false);
  const indexCAPCaseLaw = async () => {
    return axios
      .post(`${getGideonApiUrl()}/v1/cap/case/index`, {
        cap_ids: [Number(caseNumber)],
      })
      .then(() => setCaseNumber(""));
  };
  // RENDER
  return (
    <StyledCAPCaseLawDriver>
      <div className="driver__lead">
        <div className="driver__lead__text">
          <button onClick={() => navigate("/")}>⬅</button>
          <h2>U. S. Caselaw Search</h2>
        </div>
      </div>
      <div className="driver__toggle-details">
        <small>Source: Caselaw Access Project</small>
        <small className="" onClick={() => setShowDetails(!showDetails)}>
          {showDetails ? "Hide" : "Show"} Details
        </small>
      </div>

      {showDetails ? (
        <div className="driver__details">
          <div className="cap-indexer">
            <table>
              <tbody>
                <tr>
                  <td>
                    <label htmlFor="case-selector">Index CAP Caselaw ID</label>
                  </td>
                  <td>
                    <input id="case-selector" value={caseNumber} onChange={(e) => setCaseNumber(e.target.value)} />
                  </td>
                  <td>
                    <button onClick={() => indexCAPCaseLaw()}>+ Index Case</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </StyledCAPCaseLawDriver>
  );
};

const StyledCAPCaseLawDriver = styled(StyledDriverBox)`
  .cap-indexer {
    display: flex;
  }
`;
