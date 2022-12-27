import React, { useState } from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { useCase, useCaseUpdate, useCaseUserUpdate } from "../data/useCase";
import { useOrganizations } from "../data/useOrganizations";
import { CaseAdminToolbox } from "./CaseAdminToolbox";
import { ConfirmDeleteButton } from "./ConfirmDeleteButton";

export const CaseDriver: React.FC<{ caseId: number }> = ({ caseId }) => {
  const navigate = useNavigate();
  const [showDetails, setShowDetails] = useState(false);
  const [userIdToAdd, setUserIdToAdd] = useState<String>("");
  const { data: cse } = useCase(caseId);
  const { mutateAsync: caseUpdate } = useCaseUpdate();
  const { mutateAsync: caseUserUpdate } = useCaseUserUpdate();
  const { data: organizations } = useOrganizations();
  const focusedOrg = organizations?.find((o) => o.id === cse?.organization_id);

  // RENDER
  return !cse ? null : (
    <StyledCaseDriver onMouseLeave={() => setShowDetails(false)}>
      <div className="case-driver__lead">
        <div className="case-driver__lead__text">
          <button onClick={() => navigate("/cases")}>⬅</button>
          <input value={cse.name} onChange={(e) => caseUpdate({ id: cse.id, name: e.target.value })} />
        </div>
      </div>
      <div className="case-driver__toggle-details">
        <small>Attorneys 👩‍💼: {cse.users.map((u) => u.name).join(", ")}</small>
        <small className="" onClick={() => setShowDetails(!showDetails)}>
          {showDetails ? "Hide" : "Show"} Details
        </small>
      </div>
      {showDetails ? (
        <div className="case-driver__staff">
          <table>
            <thead>
              <tr>
                <th>User</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <select defaultValue="" onChange={(e) => setUserIdToAdd(e.target.value)}>
                    <option value="">--- Select User to Add --</option>
                    {focusedOrg?.users
                      ?.filter((u) => !cse.users.some((user) => user.id === u.id))
                      ?.map((u) => (
                        <option key={u.id} value={u.id}>
                          {u.name}
                        </option>
                      ))}
                  </select>
                </td>
                <td>
                  <button
                    onClick={() => caseUserUpdate({ action: "add", case_id: cse.id, user_id: Number(userIdToAdd) })}
                  >
                    + Add
                  </button>
                </td>
              </tr>
              {cse.users.map((u) => (
                <tr key={u.id}>
                  <td>{u.name}</td>
                  <td>
                    <ConfirmDeleteButton
                      prompts={["Remove", "Yes, Remove"]}
                      onClick={() => caseUserUpdate({ action: "remove", case_id: cse.id, user_id: Number(u.id) })}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <hr />
          <CaseAdminToolbox caseId={cse.id} />
        </div>
      ) : null}
    </StyledCaseDriver>
  );
};

const StyledCaseDriver = styled.div`
  background: white;
  border-radius: 4px;
  margin: 12px;
  padding: 0;
  & > div {
    padding: 12px 0;
  }
  .case-driver__lead {
    display: flex;
    align-items: center;
    button {
      margin: 0 12px;
    }
    .case-driver__lead__text {
      width: 100%;
      display: flex;
      button {
        position: relative;
        left: -54px;
      }
      input {
        width: auto;
        flex-grow: 1;
        margin-left: -40px;
        margin-right: 12px;
        font-size: 16px;
        padding: 4px;
        font-weight: 700;
      }
    }
  }
  .case-driver__toggle-details {
    font-size: 12px;
    opacity: 0.5;
    cursor: pointer;
    padding: 0 12px 12px;
    display: flex;
    justify-content: space-between;
  }
  .case-driver__staff {
    padding: 0 12px 12px;
    table,
    thead,
    tbody {
      width: 100%;
      text-align: left;
    }
    table {
      margin: 0;
    }
    th,
    td,
    button {
      font-size: 13px;
    }
    th {
      font-weight: 900;
    }
    td select {
      width: 100%;
    }
    td button {
      width: 100%;
    }
    tr > td:first-of-type,
    tr > th:first-of-type {
      width: 80%;
    }
  }
`;
