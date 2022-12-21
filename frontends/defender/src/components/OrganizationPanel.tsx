import React from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { useAppStore } from "../data/AppStore";
import { TOrganization } from "../data/useOrganizations";
import { TUser } from "../data/useUser";

export const OrganizationPanel: React.FC<{ allowNavigate?: boolean; organization: TOrganization }> = ({
  allowNavigate,
  organization,
}) => {
  const app = useAppStore();
  const navigate = useNavigate();

  // RENDER
  return (
    <StyledOrganizationPanel>
      <h2>Name: {organization.name}</h2>
      <p>{organization?.users?.map((u) => u.name).join(", ")}</p>
      {allowNavigate === true && (
        <button
          onClick={() => {
            app.setFocusedOrgId(organization.id);
            navigate("/cases");
          }}
        >
          Go to Organization
        </button>
      )}
    </StyledOrganizationPanel>
  );
};

const StyledOrganizationPanel = styled.div`
  background: white;
  border-radius: 6px;
  padding: 24px;
  h2 {
    font-size: 20px;
    font-weight: 900;
  }
  p {
    margin: 12px 0;
  }
`;
