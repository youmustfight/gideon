import { useState } from "react";
import { Link } from "react-router-dom";
import styled from "styled-components";
import { reqQueryWritingSimilarity } from "../data/useQueryAI";
import { TWritingCreateParams, useWritingCreate } from "../data/useWriting";
import { TWriting, useWritings } from "../data/useWritings";
import { SlimBox } from "./styled/StyledBox";

type TWritingsBoxProps = {
  caseId?: number;
  isTemplate: boolean;
  organizationId?: number;
};

export const WritingsBox: React.FC<TWritingsBoxProps> = ({ caseId, isTemplate, organizationId }) => {
  const { data: writings } = useWritings({ caseId, isTemplate: isTemplate, organizationId });
  const { data: writingsTemplates } = useWritings({ isTemplate: true, organizationId });
  const { mutateAsync: writingCreate } = useWritingCreate();
  const [selectedTemplateId, setSelectedTemplateId] = useState("");
  // --- create helper
  const onWritingCreate = (runAIWriter: boolean) => {
    const writingParams: TWritingCreateParams = {
      caseId,
      isTemplate,
      name: prompt(isTemplate ? "Template Name:" : "Writing File Name:") ?? "",
      organizationId,
      forkedWritingId: selectedTemplateId ? Number(selectedTemplateId) : undefined,
    };
    if (selectedTemplateId) {
      const templateToUse = writingsTemplates?.find((wt) => Number(wt.id) === Number(selectedTemplateId));
      writingParams.bodyHtml = templateToUse?.body_html;
      writingParams.bodyText = templateToUse?.body_text;
    }
    writingCreate({ params: writingParams, runAIWriter });
  };
  // --- search helper
  const [searchQueryWriting, setSearchQueryWriting] = useState<string>("");
  const [similarWritingIds, setSimilarWritingIds] = useState<number[]>();
  const searchQueryWritingHelper = async () => {
    const { locations } = await reqQueryWritingSimilarity({ caseId, query: searchQueryWriting });
    // @ts-ignore
    setSimilarWritingIds(locations?.map((l) => l.writing_id));
  };
  const clearSearch = () => {
    setSearchQueryWriting("");
    setSimilarWritingIds(undefined);
  };

  // RENDER
  return (
    <div>
      <StyledWritingsBoxLead>
        <h2>{isTemplate ? "Templates" : "Writings"}</h2>
        <div>
          <select value={selectedTemplateId} onChange={(e) => setSelectedTemplateId(e.target.value)}>
            <option value="">--- Without Template ---</option>
            {writingsTemplates?.map((wt) => (
              <option key={wt.id} value={wt.id}>
                Template: {wt.name}
              </option>
            ))}
          </select>
          <button onClick={() => onWritingCreate(false)}>{isTemplate ? "+ Template" : "+ Add"}</button>
          {!isTemplate && <button onClick={() => onWritingCreate(true)}>+ Fill with AI</button>}
        </div>
      </StyledWritingsBoxLead>
      <StyledWritingsBoxSearch>
        <form onSubmit={(e) => e.preventDefault()}>
          <input
            placeholder="Search writings..."
            value={searchQueryWriting}
            onChange={(e) => setSearchQueryWriting(e.target.value)}
          />
          <button type="submit" disabled={!searchQueryWriting} onClick={searchQueryWritingHelper}>
            Search
          </button>
          <button onClick={clearSearch}>Clear</button>
        </form>
      </StyledWritingsBoxSearch>
      {writings && (
        <StyledWritingsBox>
          {(similarWritingIds
            ? similarWritingIds
                .map((writingId) => writings.find((w) => w.id === writingId))
                .filter((wr) => wr !== undefined)
            : writings
          )?.map((w: any) => (
            <SlimBox key={w.id}>
              <p>
                <Link to={caseId ? `/case/${caseId}/writing/${w.id}` : `/writing/${w.id}`}>{w.name ?? "Untitled"}</Link>
              </p>
            </SlimBox>
          ))}
        </StyledWritingsBox>
      )}
    </div>
  );
};

const StyledWritingsBoxLead = styled.div`
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
  form {
    display: flex;
    justify-content: flex-end;
    align-items: center;
  }
  .discovery-box__file-uploader {
    input {
      max-width: 180px;
    }
  }
`;

const StyledWritingsBoxSearch = styled.div`
  margin: 0 4px;
  form {
    display: flex;
    width: 100%;
  }
  input {
    width: 100%;
  }
`;

const StyledWritingsBox = styled.div`
  margin: 8px 4px 20px;
  button {
    width: 100%;
  }
`;
