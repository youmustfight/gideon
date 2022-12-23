import React from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { useUserLogout } from "../../data/useUser";

export const ViewProfile = () => {
  const navigate = useNavigate();
  const { mutateAsync: logout } = useUserLogout();

  // RENDER
  return (
    <StyledViewProfile>
      <button onClick={() => navigate("/organizations")}>Go to Organizations</button>
      <br />
      <button onClick={() => logout()}>Logout</button>
    </StyledViewProfile>
  );
};

const StyledViewProfile = styled.div`
  padding: 36px 24px;
  display: flex;
  flex-direction: column;
`;
