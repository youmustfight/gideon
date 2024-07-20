import React from "react";
import styled from "styled-components";
import { BriefEditor } from "../../components/BriefEditor/BriefEditor";
import { DiscoveryBox } from "../../components/DiscoveryBox";
import { TimelineSummary } from "../../components/TimelineSummary";
import { WritingsBox } from "../../components/WritingsBox";
import { useAppStore } from "../../data/AppStore";
import { AIRequestBox } from "../../components/AIRequest/AIRequestBox";

export const ViewCaseOverview = () => {
  const { focusedCaseId, focusedOrgId } = useAppStore();

  // RENDER (attaching key to force re-renders of child components, so we don't have lingering react-query data)
  return !focusedCaseId ? null : (
    <>
      <AIRequestBox />
      <StyledViewCaseOverview key={focusedCaseId}>
        {/* LEGAL BRIEF */}
        <section>
          <BriefEditor caseId={focusedCaseId} />
        </section>

        <section>
          {/* --- discovery */}
          <DiscoveryBox caseId={focusedCaseId} />
          {/* --- writings */}
          <WritingsBox caseId={focusedCaseId} isTemplate={false} organizationId={focusedOrgId} />
        </section>
      </StyledViewCaseOverview>
    </>
  );
};

const StyledViewCaseOverview = styled.div`
  padding-top: 24px;
  padding-bottom: 24px;
  .my-docs {
    margin: 12px;
    text-align: center;
    font-size: 11px;
    opacity: 0.5;
  }
  h4 {
    opacity: 0.8;
  }
`;
