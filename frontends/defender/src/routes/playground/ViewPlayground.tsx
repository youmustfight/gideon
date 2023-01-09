import React, { useEffect } from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { AIRequestBox, StyledAIRequestBox } from "../../components/AIRequest/AIRequestBox";
import { useAppStore } from "../../data/AppStore";

export const ViewPlayground = () => {
  const navigate = useNavigate();
  const { focusedOrgId } = useAppStore();
  // ON MOUNT
  useEffect(() => {
    // --- if focused on an org navigate to the cases view
    if (focusedOrgId) navigate("/cases");
  }, []);

  // RENDER
  return (
    <StyledViewPlayground>
      <div className="playground__centerpiece">
        <p>Summarize, Ask, Write</p>
        <AIRequestBox forceInitialAiRequestType={"summarize"} />
      </div>
    </StyledViewPlayground>
  );
};

const StyledViewPlayground = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 90vh;
  padding: 24px;
  .playground__centerpiece {
    width: 100%;
    margin-bottom: 64px;
    & > p {
      text-align: center;
      margin-bottom: 12px;
    }
    ${StyledAIRequestBox} {
      flex-grow: 1;
    }
  }
`;
