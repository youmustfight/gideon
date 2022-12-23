import React from "react";
import styled from "styled-components";
import { OrganizationPanel } from "../../components/OrganizationPanel";
import { useOrganizations } from "../../data/useOrganizations";

export const ViewOrganizations = () => {
  const { data: organizations } = useOrganizations();

  // RENDER
  return (
    <StyledViewOrganizations>
      {organizations?.map((org) => (
        <OrganizationPanel key={org.id} allowNavigate organization={org} />
      ))}
    </StyledViewOrganizations>
  );
};

const StyledViewOrganizations = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: space-between;
`;
