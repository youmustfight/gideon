import React from "react";
import styled from "styled-components";

export const ToolWindow: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <StyledToolWindow>
      <main>{children}</main>
    </StyledToolWindow>
  );
};

const StyledToolWindow = styled.div`
  z-index: -10;
  min-height: 100vh;
  background: #f1f4f8;
  display: flex;
  & > main {
    z-index: 0;
    height: 100%;
    min-height: 100vh;
    width: 100%;
    max-width: 640px;
    margin: 0 auto;
    flex-grow: 1;
  }
`;
