import { useEffect } from "react";
import { Routes, Route, useParams } from "react-router";
import styled from "styled-components";
import { CaseAdminToolbox } from "../../components/CaseAdminToolbox";
import { CaseDriver } from "../../components/CaseDriver";
import { useAppStore } from "../../data/AppStore";
import { ViewCaseDocument } from "./ViewCaseDocument";
import { ViewCaseOverview } from "./ViewCaseOverview";
import { ViewWriting } from "../writing/ViewWriting";

export const ViewCase = () => {
  const params = useParams();
  const caseId = Number(params.caseId);
  const app = useAppStore();
  // ON MOUNT
  // --- on mounting this, set the new focus
  useEffect(() => {
    if (caseId) app.setFocusedCaseId(Number(caseId));
  }, []);

  // RENDER
  return !caseId ? null : (
    <>
      <CaseDriver caseId={caseId} />
      <StyledViewCase>
        {/* --- CASE VIEWS ---  */}
        <Routes>
          {/* --- document inspection */}
          <Route path="/document/:documentId" element={<ViewCaseDocument />} />
          {/* --- writing */}
          <Route path="/writing/:writingId" element={<ViewWriting caseId={caseId} />} />
          {/* --- overview */}
          <Route path="/" element={<ViewCaseOverview />} />
          {/* --- default overview showing. TODO: figure out relative path version */}
          {/* <Route path="/*" element={<Navigate to={`/case/${caseId}/overview`} />} /> */}
        </Routes>
      </StyledViewCase>
    </>
  );
};

const StyledViewCase = styled.div`
  margin-top: 20px;
  a,
  a:active a:visited,
  a:hover {
    color: blue !important;
    text-decoration: none;
  }
  a:hover {
    text-decoration: underline;
  }
  .section-lead {
    display: flex;
    flex-direction: column;
    text-align: left;
    padding: 0 16px;
    margin: 4px 20px;
    h2 {
      font-size: 20px;
      font-weight: 900;
      margin: 6px 0;
    }
    h3,
    h4 {
      font-weight: 900;
      margin: 6px 0;
      display: flex;
    }
    h2,
    h3,
    h4 {
      justify-content: center;
    }
  }
  section {
    box-shadow: rgb(0 0 0 / 4%) 0px 0 60px 0px;
    border-radius: 4px;
    padding: 12px;
    margin: 10px 12px;
    &:first-of-type {
      margin-top: 0;
    }
    &:last-of-type {
      margin-bottom: 0;
    }
    ul {
      list-style-type: disc;
      padding-left: 12px;
      li {
        font-size: 13px;
        margin: 3px 0;
      }
    }
    &.no-shadow {
      box-shadow: none;
    }
  }
  .section-people {
    span.person-pill {
      margin: 0 6px 0 0;
    }
  }
  .section-admin {
    padding: 1em;
    display: flex;
    text-align: center;
    flex-direction: column;
  }
`;
