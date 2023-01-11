import React from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { AppHeader } from "../../components/AppHeader";
import { StyledViewCase } from "../../components/styled/StyledViewCase";
import { reqUserAILocksReset, useUser, useUserLogout } from "../../data/useUser";

export const ViewProfile = () => {
  const { mutateAsync: logout } = useUserLogout();
  const { data: user } = useUser();

  // RENDER
  return (
    <>
      <StyledViewProfile>
        <div className="section-lead">
          <h3>Logged in as {user?.email}</h3>
        </div>
        <section>
          <button style={{ width: "100%" }} onClick={() => reqUserAILocksReset(user!.id)}>
            Reset AI Action Locks
          </button>
        </section>
        <section>
          <button style={{ width: "100%" }} onClick={() => logout()}>
            Logout
          </button>
        </section>
      </StyledViewProfile>
    </>
  );
};

const StyledViewProfile = styled(StyledViewCase)`
  padding: 36px 24px;
`;
