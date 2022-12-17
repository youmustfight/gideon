import React, { useState } from "react";
import { useDebounce } from "react-use";
import styled from "styled-components";
import { useCaseFactCreate, useCaseFactDelete, useCaseFacts, useCaseFactUpdate } from "../data/useCaseFact";
import { SlimBox } from "./styled/StyledBox";

const CaseFactBox = ({ caseFact, caseId }) => {
  const [newCaseFactText, setNewCaseFactText] = useState(caseFact.text ?? "");
  const { mutateAsync: caseFactUpdate } = useCaseFactUpdate();
  const { mutateAsync: caseFactDelete } = useCaseFactDelete();
  useDebounce(() => caseFactUpdate({ id: caseFact.id, caseId, text: newCaseFactText }), 1000 * 2, [newCaseFactText]);

  // RENDER
  return (
    <SlimBox>
      <input value={newCaseFactText} onChange={(e) => setNewCaseFactText(e.target.value)} style={{ width: "100%" }} />
      <div>
        <button onClick={() => caseFactDelete(caseFact.id)}>Delete</button>
      </div>
    </SlimBox>
  );
};

export const CaseFacts: React.FC<{ caseId: number }> = ({ caseId }) => {
  const { data: caseFacts } = useCaseFacts({ caseId });
  const { mutateAsync: caseFactCreate } = useCaseFactCreate({ caseId });
  // RENDER
  return (
    <>
      <StyledCaseFactsBoxLead>
        <h2>Case Facts</h2>
        <button onClick={() => caseFactCreate()}>+ Case Fact</button>
      </StyledCaseFactsBoxLead>
      <StyledCaseFactsBox>
        {caseFacts?.map((cf) => (
          <CaseFactBox key={cf.id} caseId={caseId} caseFact={cf} />
        ))}
      </StyledCaseFactsBox>
    </>
  );
};

const StyledCaseFactsBoxLead = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
  margin-bottom: 12px;
  padding: 4px;
  h2 {
    font-size: 18px;
    font-weight: 900;
  }
`;
const StyledCaseFactsBox = styled.div``;
