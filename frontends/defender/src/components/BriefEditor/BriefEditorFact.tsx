import { useState } from "react";
import styled from "styled-components";
import { TBriefFact } from "../../data/useBrief";
import { TQueryLocation, reqQueryDocumentLocations } from "../../data/useQueryAI";
import { ConfirmButton } from "../ConfirmButton";
import { DocumentContentLocationBox } from "../DocumentContentLocationBox";
import { SlimBox } from "../styled/StyledBox";

type TBriefEditorFactProps = {
  briefFact: TBriefFact;
  caseId: number;
  onChange: (newFactValue: TBriefFact) => void;
  onDelete: (factToDelete: TBriefFact) => void;
};

export const BriefEditorFact: React.FC<TBriefEditorFactProps> = ({ briefFact, caseId, onChange, onDelete }) => {
  // SETUP
  const [isEditing, setIsEditing] = useState(briefFact?.text?.length === 0);
  const [fact, setFact] = useState(briefFact);
  // --- update handler
  const updateHandler = (updates: Partial<TBriefFact>) => {
    const newFact = { ...fact, ...updates };
    setFact(newFact);
    onChange(newFact);
  };
  // --- location search
  const [briefFactLocations, setBriefFactLocations] = useState<TQueryLocation[]>();
  const [isSearchingForFactLocations, setIsSearchingForFactLocations] = useState(false);
  const searchForLocations = () => {
    setIsSearchingForFactLocations(true);
    reqQueryDocumentLocations({ caseId, query: briefFact.text }).then(({ locations }) => {
      setBriefFactLocations(locations);
      setIsSearchingForFactLocations(false);
    });
  };

  // RENDER
  return isEditing ? (
    <div>
      <StyledBriefFactSlimBox>
        <textarea value={fact.text} rows={7} onChange={(e) => updateHandler({ text: e.target.value })} />
        <div className="fact-edit__actions">
          <button onClick={() => setIsEditing(false)}>Done</button>
          <ConfirmButton prompts={["Delete", "Yes, Delete Fact"]} onClick={() => onDelete(briefFact)} />
        </div>
      </StyledBriefFactSlimBox>
      {/* TODO: make DRY */}
      {briefFactLocations && (
        <>
          <hr />
          <button onClick={() => setBriefFactLocations(undefined)} style={{ width: "100%" }}>
            Clear References Search
          </button>
          {briefFactLocations?.map((location) => (
            <DocumentContentLocationBox key={Object.values(location).join("-")} location={location} />
          ))}
        </>
      )}
    </div>
  ) : (
    <div>
      <p>
        <span>{briefFact.text}</span> <u onClick={() => setIsEditing(true)}>Edit</u>{" "}
        <u onClick={searchForLocations}>{isSearchingForFactLocations ? "Searching..." : "See References"}</u>
      </p>
      {/* TODO: make DRY */}
      {briefFactLocations && (
        <>
          <hr />
          <button onClick={() => setBriefFactLocations(undefined)} style={{ width: "100%" }}>
            Clear References Search
          </button>
          {briefFactLocations?.map((location) => (
            <DocumentContentLocationBox key={Object.values(location).join("-")} location={location} />
          ))}
        </>
      )}
    </div>
  );
};

const StyledBriefFactSlimBox = styled(SlimBox)`
  flex-direction: column;
  hr {
    width: 100%;
  }
  .fact-edit__actions {
    display: flex;
    justify-content: space-between;
    margin-top: 4px;
  }
  textarea {
    font-size: 13px !important;
  }
`;
