import React from "react";
import styled from "styled-components";
import { AppHeader } from "../../components/AppHeader";
import { OrganizationDriver } from "../../components/OrganizationDriver";
import { StyledViewCase } from "../../components/styled/StyledViewCase";
import { useOrganizationCreate, useOrganizations } from "../../data/useOrganizations";

export const ViewOrganizations = () => {
  const { data: organizations } = useOrganizations();
  const { mutateAsync: orgCreate } = useOrganizationCreate();

  // RENDER
  return (
    <>
      <AppHeader />
      <StyledViewOrganizations>
        <div className="section-lead">
          <h3>All Organizations</h3>
        </div>
        {organizations?.map((org) => (
          <OrganizationDriver key={org.id} allowNavigate organization={org} />
        ))}
        <section>
          <button
            onClick={() =>
              orgCreate({
                name: prompt("Name of Org:") ?? "",
              })
            }
            style={{ width: "100%" }}
          >
            + Add Organization
          </button>
        </section>
      </StyledViewOrganizations>
    </>
  );
};

const StyledViewOrganizations = styled(StyledViewCase)`
  padding: 36px 24px;
`;
