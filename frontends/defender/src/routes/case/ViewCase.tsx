import { Fragment, useEffect } from "react";
import { Routes, Route, useParams } from "react-router";
import styled from "styled-components";
import { CaseAdminToolbox } from "../../components/CaseAdminToolbox";
import { CaseDriver } from "../../components/CaseDriver";
import { useAppStore } from "../../data/AppStore";
import { ViewCaseDocument } from "./ViewCaseDocument";
import { ViewCaseOverview } from "./ViewCaseOverview";
import { ViewWriting } from "../writing/ViewWriting";
import { StyledViewCase } from "../../components/styled/StyledViewCase";

export const ViewCase = () => {
  const params = useParams();
  const caseId = Number(params.caseId);
  const app = useAppStore();
  // ON MOUNT
  // --- on mounting this, set the new focus
  useEffect(() => {
    if (caseId) app.setFocusedCaseId(Number(caseId));
  }, [caseId]);

  // RENDER
  return !caseId ? null : (
    <Fragment key={caseId}>
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
    </Fragment>
  );
};
