import React, { useState } from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { useAppStore } from "../data/AppStore";
import { TOrganization, useOrganizationUserUpdate } from "../data/useOrganizations";
import { TUser, useUser, useUserUpdate } from "../data/useUser";
import { ConfirmDeleteButton } from "./ConfirmDeleteButton";

export const OrganizationDriver: React.FC<{ allowNavigate?: boolean; organization: TOrganization }> = ({
  allowNavigate,
  organization,
}) => {
  const navigate = useNavigate();
  const app = useAppStore();
  const { data: user } = useUser();
  const { mutateAsync: updateUser } = useUserUpdate();
  const { mutateAsync: updateOrganizationUser } = useOrganizationUserUpdate();
  const [showDetails, setShowDetails] = useState(false);

  // RENDER
  return (
    <StyledOrganizationDriver>
      <div className="org-driver__lead">
        <div className="org-driver__lead__text">
          <h5>{organization.name}</h5>
        </div>
        {allowNavigate === true ? (
          <button
            onClick={() => {
              app.setFocusedOrgId(organization.id);
              navigate("/cases");
            }}
          >
            Go&nbsp;to&nbsp;Organization
          </button>
        ) : null}
      </div>
      <div className="org-driver__toggle-details">
        <small>Attorneys 👩‍💼: {organization?.users.map((u) => u.name).join(", ")}</small>
        <small className="" onClick={() => setShowDetails(!showDetails)}>
          {showDetails ? "Hide" : "Show"} Details
        </small>
      </div>
      {showDetails && (
        <div className="org-driver__staff">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Set Password</th>
                <th>Is Admin</th>
                <th className="row-actions">
                  <button
                    onClick={() =>
                      updateOrganizationUser({
                        action: "add",
                        // @ts-ignore
                        organization_id: app.focusedOrgId,
                        user: { email: prompt("User Email:")?.trim(), name: prompt("User Name:")?.trim() },
                      })
                    }
                  >
                    + Add
                  </button>
                </th>
              </tr>
            </thead>
            <tbody>
              {organization?.users?.map((u) => (
                <tr key={u.id}>
                  <td>
                    <form
                      onSubmit={(e: any) => {
                        e.preventDefault();
                        const name = new FormData(e.target).get("name");
                        if (typeof name === "string" && name.length > 0) {
                          updateUser({ id: u.id, name });
                          e.target.elements["name"].value = "";
                        }
                      }}
                    >
                      <input type="text" defaultValue={u.name} name="name" />
                      <button>Save</button>
                    </form>
                  </td>
                  <td>{u.email}</td>
                  <td>
                    <form
                      onSubmit={(e: any) => {
                        e.preventDefault();
                        const password = new FormData(e.target).get("password");
                        if (typeof password === "string" && password.length > 0) {
                          updateUser({ id: u.id, password });
                          e.target.elements["password"].value = "";
                        }
                      }}
                    >
                      <input type="password" name="password" />
                      <button>Save</button>
                    </form>
                  </td>
                  <td>
                    <input disabled type="checkbox" />
                  </td>
                  <td className="row-actions">
                    <ConfirmDeleteButton
                      disabled={user?.id === u.id || !app.focusedOrgId}
                      prompts={user?.id === u.id ? ["You"] : ["Remove", "Yes, Remove"]}
                      onClick={() =>
                        updateOrganizationUser({ action: "remove", organization_id: app.focusedOrgId!, user_id: u.id })
                      }
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </StyledOrganizationDriver>
  );
};

const StyledOrganizationDriver = styled.div`
  background: white;
  border-radius: 6px;
  margin: 12px;
  padding: 0 !important;
  .org-driver__lead {
    display: flex;
    align-items: center;
    button {
      margin: 0 12px;
    }
  }
  .org-driver__lead__text {
    display: flex;
    align-items: center;
    padding: 12px;
    width: 100%;
    h5 {
      font-size: 16px;
      font-weight: 900;
    }
    small {
      cursor: pointer;
      margin: 0 8px;
      font-size: 12px;
      text-decoration: underline;
      opacity: 0.5;
    }
  }
  .org-driver__toggle-details {
    font-size: 12px;
    opacity: 0.5;
    cursor: pointer;
    padding: 0 12px 12px;
    display: flex;
    justify-content: space-between;
  }
  .org-driver__staff {
    border-top: 1px solid #ddd;
    padding: 0 12px 12px;
    table,
    thead,
    tbody {
      width: 100%;
      text-align: left;
    }
    table {
      margin: 18px 0 0;
    }
    th,
    td,
    button {
      font-size: 13px;
    }
    th {
      font-weight: 900;
    }
    form {
      display: flex;
      input {
        max-width: 100px;
      }
    }
    .row-actions {
      text-align: right;
      width: 100px;
      max-width: 100px;
    }
    p {
      margin: 12px 0;
    }
  }
`;
