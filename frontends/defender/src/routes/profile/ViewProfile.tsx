import React from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { OrganizationDriver } from "../../components/OrganizationDriver";
import { StyledViewCase } from "../../components/styled/StyledViewCase";
import { useOrganizations } from "../../data/useOrganizations";
import { useUser, useUserLogout } from "../../data/useUser";

export const ViewProfile = () => {
  const navigate = useNavigate();
  const { mutateAsync: logout } = useUserLogout();
  const { data: organizations } = useOrganizations();
  const { data: user } = useUser();

  // RENDER
  return (
    <StyledViewProfile>
      <div className="section-lead">
        <h3 onClick={() => navigate("/organizations")}>Organizations</h3>
      </div>
      {organizations
        ?.filter((o) => o.users?.some((u) => u.id === user.id))
        ?.map((org) => (
          <OrganizationDriver key={org.id} allowNavigate organization={org} />
        ))}
      <div className="section-lead">
        <h3>Logged in as {user?.email}</h3>
      </div>
      <section>
        <button style={{ width: "100%" }} onClick={() => logout()}>
          Logout
        </button>
      </section>
    </StyledViewProfile>
  );
};

const StyledViewProfile = styled(StyledViewCase)`
  padding: 36px 24px;
`;
