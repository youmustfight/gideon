import React from "react";
import styled from "styled-components";
import { DiscoveryBox } from "../../components/DiscoveryBox";
import { HighlightsBox } from "../../components/HighlightsBox";
import { TimelineSummary } from "../../components/TimelineSummary";
import { useHighlights } from "../../data/useHighlights";

export const ViewCaseOverview = () => {
  const { data: highlights = [] } = useHighlights();
  // RENDER
  return (
    <>
      <StyledViewCaseOverview>
        {/* SUMMATION (timeline w/ summaries) */}
        <div className="section-lead">
          <h4>Timeline Summary</h4>
        </div>
        <section>
          <TimelineSummary />
        </section>

        {/* DISCOVERY/INDEXED DOCS + UPLOAD */}
        <div className="section-lead">
          <h4>Discovery, Evidence, Exhibits</h4>
        </div>
        <section>
          <DiscoveryBox />
        </section>

        {/* TODO: MY DOCS */}

        {/* HIGHLIGHTS/ANNOTATIONS */}
        {highlights?.length > 0 ? (
          <>
            <div className="section-lead">
              <h4>Highlights</h4>
            </div>
            <section>
              <HighlightsBox />
            </section>
          </>
        ) : null}
      </StyledViewCaseOverview>
    </>
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
