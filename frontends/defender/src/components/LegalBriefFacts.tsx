import React, { useState } from "react";
import { useDebounce } from "react-use";
import styled from "styled-components";
import {
  TLegalBriefFact,
  useLegalBriefFactCreate,
  useLegalBriefFactDelete,
  useLegalBriefFacts,
  useLegalBriefFactUpdate,
} from "../data/useLegalBriefFact";
import { TQueryLocation } from "../data/useDocuments";
import { reqQueryDocumentLocations } from "../data/useQueryAI";
import { ConfirmDeleteButton } from "./ConfirmDeleteButton";
import { LocationBox } from "./LocationBox";
import { SlimBox } from "./styled/StyledBox";

const LegalBriefFactBox: React.FC<{ legalBriefFact: TLegalBriefFact; caseId: number }> = ({
  legalBriefFact,
  caseId,
}) => {
  const [newLegalBriefFactText, setNewLegalBriefFactText] = useState(legalBriefFact.text ?? "");
  const [legalBriefFactLocations, setLegalBriefFactLocations] = useState<TQueryLocation[]>();
  const { mutateAsync: legalBriefFactUpdate } = useLegalBriefFactUpdate();
  const { mutateAsync: legalBriefFactDelete } = useLegalBriefFactDelete();
  useDebounce(() => legalBriefFactUpdate({ id: legalBriefFact.id, caseId, text: newLegalBriefFactText }), 1000 * 2, [
    newLegalBriefFactText,
  ]);

  // RENDER
  return (
    <StyledLegalBriefFactSlimBox>
      <div style={{ display: "flex", width: "100%" }}>
        <input
          value={newLegalBriefFactText}
          onChange={(e) => setNewLegalBriefFactText(e.target.value)}
          style={{ width: "100%" }}
        />
        <div style={{ display: "flex" }}>
          <button
            onClick={() =>
              reqQueryDocumentLocations({ caseId, query: legalBriefFact.text }).then(({ locations }) =>
                setLegalBriefFactLocations(locations)
              )
            }
          >
            Find&nbsp;Refs
          </button>
          <ConfirmDeleteButton
            prompts={["Delete", "Yes Delete"]}
            onClick={() => legalBriefFactDelete(legalBriefFact.id)}
          />
        </div>
      </div>
      {legalBriefFactLocations && (
        <>
          <hr />
          <button onClick={() => setLegalBriefFactLocations(undefined)}>Clear References Search</button>
          {legalBriefFactLocations?.map((location) => (
            <LocationBox location={location} />
          ))}
        </>
      )}
    </StyledLegalBriefFactSlimBox>
  );
};

export const LegalBriefFacts: React.FC<{ caseId: number }> = ({ caseId }) => {
  const { data: legalBriefFacts } = useLegalBriefFacts({ caseId });
  const { mutateAsync: legalBriefFactCreate } = useLegalBriefFactCreate({ caseId });
  // RENDER
  return (
    <>
      <StyledLegalBriefFactsBoxLead>
        <h2>Legal Brief - Facts</h2>
        <button onClick={() => legalBriefFactCreate()}>+ Case Fact</button>
      </StyledLegalBriefFactsBoxLead>
      <StyledLegalBriefFactsBox>
        {legalBriefFacts?.map((cf) => (
          <LegalBriefFactBox key={cf.id} caseId={caseId} legalBriefFact={cf} />
        ))}
      </StyledLegalBriefFactsBox>
    </>
  );
};

const StyledLegalBriefFactsBoxLead = styled.div`
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
const StyledLegalBriefFactsBox = styled.div``;

const StyledLegalBriefFactSlimBox = styled(SlimBox)`
  flex-direction: column;
  hr {
    width: 100%;
  }
`;
