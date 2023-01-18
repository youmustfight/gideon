import React from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { reqSystemAILocksReset } from "../../components/AIRequest/aiRequestReqs";
import { AppHeader } from "../../components/AppHeader";
import { Button } from "../../components/styled/common/Button";
import { H3 } from "../../components/styled/common/Typography";
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
          <H3>Logged in as {user?.email}</H3>
        </div>
        {user?.email?.includes("gideon.foundation") && (
          <section>
            <Button style={{ width: "100%" }} onClick={() => reqSystemAILocksReset()}>
              Set System AI Action Locks
            </Button>
          </section>
        )}
        <section>
          <Button style={{ width: "100%" }} onClick={() => reqUserAILocksReset(user!.id)}>
            Reset AI Action Locks
          </Button>
          <br />
          <br />
          <Button style={{ width: "100%" }} onClick={() => logout()}>
            Logout
          </Button>
        </section>
      </StyledViewProfile>
    </>
  );
};

const StyledViewProfile = styled(StyledViewCase)`
  padding: 36px 24px;
`;
