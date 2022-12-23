import React, { useState } from "react";
import { useNavigate } from "react-router";
import { useAppStore } from "../data/AppStore";
import { reqCaseAILocksReset, reqCaseReindexAllDocuments } from "../data/useCase";
import { CAPCaseLawDriver } from "./CAPCaseLawDriver";

export const CaseAdminToolbox: React.FC = () => {
  const navigate = useNavigate();
  const { focusedCaseId } = useAppStore();
  const [isVisible, setIsVisible] = useState(false);

  return !focusedCaseId ? null : (
    <section className="section-admin">
      <u onClick={() => setIsVisible(!isVisible)}>
        <small>Show/Hide Admin Tools</small>
      </u>
      {isVisible ? (
        <>
          <CAPCaseLawDriver />
          <button onClick={() => reqCaseAILocksReset(focusedCaseId)}>Reset AI Action Locks</button>
          <br />
          <button onClick={() => reqCaseReindexAllDocuments(focusedCaseId)}>Re-Index All Documents</button>
        </>
      ) : null}
    </section>
  );
};
