import React from "react";
import styled from "styled-components";
import { OrganizationDriver } from "../../components/OrganizationDriver";
import { useOrganizationCreate, useOrganizations } from "../../data/useOrganizations";

export const ViewOrganizations = () => {
  const { data: organizations } = useOrganizations();
  const { mutateAsync: orgCreate } = useOrganizationCreate();

  // RENDER
  return (
    <StyledViewOrganizations>
      {organizations?.map((org) => (
        <OrganizationDriver key={org.id} allowNavigate organization={org} />
      ))}
      <div className="add-orgs">
        <button
          onClick={() =>
            orgCreate({
              name: prompt("Name of Org:") ?? "",
            })
          }
        >
          + Add Organization
        </button>
      </div>
    </StyledViewOrganizations>
  );
};

const StyledViewOrganizations = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  .add-orgs {
    margin-top: 16px;
    padding: 16px;
    border-top: 1px solid #ccc;
    button {
      width: 100%;
    }
  }
`;
