import React from "react";
import styled from "styled-components";
import { LegalBriefFacts } from "../../components/LegalBriefFacts";
import { DiscoveryBox } from "../../components/DiscoveryBox";
import { TimelineSummary } from "../../components/TimelineSummary";
import { WritingsBox } from "../../components/WritingsBox";
import { useAppStore } from "../../data/AppStore";
import { InquiryBox } from "../../components/InquiryBox";

export const ViewCaseOverview = () => {
  const { focusedCaseId, focusedOrgId } = useAppStore();

  // RENDER (attaching key to force re-renders of child components, so we don't have lingering react-query data)
  return !focusedCaseId ? null : (
    <>
      <InquiryBox />
      <StyledViewCaseOverview key={focusedCaseId}>
        {/* LEGAL BRIEF */}
        <section>
          <LegalBriefFacts caseId={focusedCaseId} />
        </section>

        <br />
        <hr />
        <br />

        <section>
          {/* --- writings */}
          <WritingsBox caseId={focusedCaseId} isTemplate={false} organizationId={focusedOrgId} />
          {/* --- discovery */}
          <DiscoveryBox caseId={focusedCaseId} />
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
