import React from "react";
import styled from "styled-components";
import { CAPCaseLawDriver } from "../../components/CAPCaseLawDriver";
import { InquiryBox } from "../../components/InquiryBox";

export const ViewCaseLaw = () => {
  return (
    <StyledViewCaseLaw>
      <div className="caselaw-driver">
        <CAPCaseLawDriver />
        <InquiryBox isCaseLawSearch />
      </div>
    </StyledViewCaseLaw>
  );
};

const StyledViewCaseLaw = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 100vh;
`;
