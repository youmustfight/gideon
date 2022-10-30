import React from "react";
import styled from "styled-components";
import { DiscoveryBox } from "../../components/DiscoveryBox";
import { HighlightsBox } from "../../components/HighlightsBox";
import { useHighlights } from "../../data/useHighlights";

export const ViewCaseOverview = () => {
  const { data: highlights = [] } = useHighlights();
  // RENDER
  return (
    <StyledViewCaseOverview>
      {/* DISCOVERY/INDEXED DOCS + UPLOAD */}
      <div className="section-lead">
        <h4>Discovery, Evidence, Exhibits</h4>
      </div>
      <section>
        <DiscoveryBox />
      </section>

      {/* TODO: SUMMATION (timeline w/ summaries) */}

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