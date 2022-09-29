import React from "react";
import styled from "styled-components";
import { DiscoveryBox } from "./components/DiscoveryBox";
import { HighlightsBox } from "./components/HighlightsBox";
import { useHighlights } from "./data/useHighlights";

export const GideonCaseView = () => {
  const { data: highlights = [] } = useHighlights();
  // RENDER
  return (
    <StyledGideonCaseView>
      {/* DISCOVERY/INDEXED DOCS + UPLOAD */}
      <div className="section-lead">
        <h4>Discovery, Evidence, Exhibits</h4>
      </div>
      <section>
        <DiscoveryBox />
      </section>

      {/* MY DOCS */}
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
    </StyledGideonCaseView>
  );
};

const StyledGideonCaseView = styled.div`
  padding-bottom: 40px;
  .my-docs {
    margin: 12px;
    text-align: center;
    font-size: 11px;
    opacity: 0.5;
  }
`;
