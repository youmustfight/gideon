import React from "react";
import { Routes, Route, useParams } from "react-router";
import styled from "styled-components";
import { AppHeader } from "../../components/AppHeader";
import { CAPCaseLawDriver } from "../../components/CAPCaseLawDriver";
import { InquiryBox } from "../../components/InquiryBox";
import { StyledViewCase } from "../../components/styled/StyledViewCase";
import { ViewCapCase } from "./ViewCapCase";

export const ViewCaseLaw = () => {
  return (
    <>
      <AppHeader />
      <div className="caselaw-driver">
        <CAPCaseLawDriver />
        <InquiryBox isCaseLawSearch />
      </div>
      <StyledViewCaseLaw>
        <Routes>
          {/* --- document inspection */}
          <Route path="/cap/:capId" element={<ViewCapCase />} />
        </Routes>
      </StyledViewCaseLaw>
    </>
  );
};

const StyledViewCaseLaw = styled(StyledViewCase)`
  margin-top: 20px;
`;
