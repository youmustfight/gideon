import { useState } from "react";
import { Link } from "react-router-dom";
import styled from "styled-components";
import { TWritingCreateParams, useWritingCreate } from "../data/useWriting";
import { useWritings } from "../data/useWritings";
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
      <StyledWritingsBox>
        {writings?.map((w) => (
          <SlimBox key={w.id}>
            <p>
              <Link to={caseId ? `/case/${caseId}/writing/${w.id}` : `/writing/${w.id}`}>{w.name ?? "Untitled"}</Link>
            </p>
          </SlimBox>
        ))}
      </StyledWritingsBox>
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

const StyledWritingsBox = styled.div`
  margin: 20px 4px;
  button {
    width: 100%;
  }
`;
