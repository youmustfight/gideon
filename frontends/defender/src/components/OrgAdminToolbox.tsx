import React, { useState } from "react";
import styled from "styled-components";
import { reqOrganizationAILocksReset } from "../data/useOrganizations";

export const OrganizationAdminToolbox: React.FC<{ organizationId?: number }> = ({ organizationId }) => {
  const [isVisible, setIsVisible] = useState(false);
  // RENDER
  return !organizationId ? null : (
    <StyledOrganizationAdminToolbox>
      <u onClick={() => setIsVisible(!isVisible)}>
        <small>Show/Hide Admin Tools</small>
      </u>
      {isVisible ? (
        <div>
          <button onClick={() => reqOrganizationAILocksReset(organizationId)}>Reset AI Action Locks</button>
        </div>
      ) : null}
    </StyledOrganizationAdminToolbox>
  );
};

const StyledOrganizationAdminToolbox = styled.div`
  small,
  button {
    font-size: 12px;
  }
  div {
    display: flex;
    flex-direction: column;
    margin-top: 4px;
  }
`;
