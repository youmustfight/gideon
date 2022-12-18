import React, { useState } from "react";
import { useDebounce } from "react-use";
import styled from "styled-components";
import { TCaseFact, useCaseFactCreate, useCaseFactDelete, useCaseFacts, useCaseFactUpdate } from "../data/useCaseFact";
import { TQueryLocation } from "../data/useDocuments";
import { reqQueryDocumentLocations } from "../data/useQueryAI";
import { ConfirmDeleteButton } from "./ConfirmDeleteButton";
import { LocationBox } from "./LocationBox";
import { SlimBox } from "./styled/StyledBox";

const CaseFactBox: React.FC<{ caseFact: TCaseFact; caseId: number }> = ({ caseFact, caseId }) => {
  const [newCaseFactText, setNewCaseFactText] = useState(caseFact.text ?? "");
  const [caseFactLocations, setCaseFactLocations] = useState<TQueryLocation[]>();
  const { mutateAsync: caseFactUpdate } = useCaseFactUpdate();
  const { mutateAsync: caseFactDelete } = useCaseFactDelete();
  useDebounce(() => caseFactUpdate({ id: caseFact.id, caseId, text: newCaseFactText }), 1000 * 2, [newCaseFactText]);

  // RENDER
  return (
    <StyledCaseFactSlimBox>
      <div style={{ display: "flex", width: "100%" }}>
        <input value={newCaseFactText} onChange={(e) => setNewCaseFactText(e.target.value)} style={{ width: "100%" }} />
        <div style={{ display: "flex" }}>
          <button
            onClick={() =>
              reqQueryDocumentLocations({ caseId, query: caseFact.text }).then(({ locations }) =>
                setCaseFactLocations(locations)
              )
            }
          >
            Find&nbsp;Refs
          </button>
          <ConfirmDeleteButton prompts={["Delete", "Yes Delete"]} onClick={() => caseFactDelete(caseFact.id)} />
        </div>
      </div>
      {caseFactLocations && (
        <>
          <hr />
          <button onClick={() => setCaseFactLocations(undefined)}>Clear References Search</button>
          {caseFactLocations?.map((location) => (
            <LocationBox location={location} />
          ))}
        </>
      )}
    </StyledCaseFactSlimBox>
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

const StyledCaseFactSlimBox = styled(SlimBox)`
  flex-direction: column;
  hr {
    width: 100%;
  }
`;
