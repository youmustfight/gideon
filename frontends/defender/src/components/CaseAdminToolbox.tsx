import React, { useState } from "react";
import { reqCaseAILocksReset, reqCaseReindexAllDocuments } from "../data/useCase";

export const CaseAdminToolbox: React.FC<{ caseId: string | number }> = ({ caseId }) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <section className="section-admin">
      <u onClick={() => setIsVisible(!isVisible)}>
        <small>Show/Hide Admin Tools</small>
      </u>
      {isVisible ? (
        <>
          <br />
          <button onClick={() => reqCaseAILocksReset(caseId)}>Reset AI Action Locks</button>
          <br />
          <button onClick={() => reqCaseReindexAllDocuments(caseId)}>Re-Index All Documents</button>
        </>
      ) : null}
    </section>
  );
};
