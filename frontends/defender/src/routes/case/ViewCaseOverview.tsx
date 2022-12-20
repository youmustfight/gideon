import React from "react";
import styled from "styled-components";
import { LegalBriefFacts } from "../../components/LegalBriefFacts";
import { DiscoveryBox } from "../../components/DiscoveryBox";
import { TimelineSummary } from "../../components/TimelineSummary";
import { WritingsBox } from "../../components/WritingsBox";
import { useAppStore } from "../../data/AppStore";

export const ViewCaseOverview = () => {
  const { focusedCaseId, focusedOrgId } = useAppStore();

  // RENDER (attaching key to force re-renders of child components, so we don't have lingering react-query data)
  return !focusedCaseId ? null : (
    <StyledViewCaseOverview key={focusedCaseId}>
      {/* WRITINGS */}
      <section>
        <WritingsBox caseId={focusedCaseId} isTemplate={false} organizationId={focusedOrgId} />
      </section>

      {/* CASE FACTS */}
      <section>
        <LegalBriefFacts caseId={focusedCaseId} />
      </section>

      {/* DISCOVERY/INDEXED DOCS + UPLOAD */}
      <section>
        <DiscoveryBox caseId={focusedCaseId} />
      </section>

      {/* SUMMATION (timeline w/ summaries) */}
      <section>
        <TimelineSummary caseId={focusedCaseId} />
      </section>
    </StyledViewCaseOverview>
  );
};

const StyledViewCaseOverview = styled.div`
  padding-bottom: 40px;
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
