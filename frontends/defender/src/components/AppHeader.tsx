import React from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";

export const AppHeader = () => {
  const navigate = useNavigate();

  // RENDER
  return (
    <StyledAppHeader>
      <span onClick={() => navigate("/cases")}>
        <b>Gideon</b>
      </span>
      <span onClick={() => navigate("/profile")}>Profile</span>
    </StyledAppHeader>
  );
};

const StyledAppHeader = styled.header`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: -1;
  padding: 12px;
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  span {
    font-weight: 900;
    cursor: pointer;
  }
`;
