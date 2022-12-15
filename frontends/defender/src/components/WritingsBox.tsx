import { useState } from "react";
import { Link } from "react-router-dom";
import styled from "styled-components";
import { TWritingCreateParams, useWritingCreate } from "../data/useWriting";
import { useWritings } from "../data/useWritings";

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
  const onWritingCreate = (e) => {
    e.preventDefault();
    const writingParams: TWritingCreateParams = {
      caseId,
      isTemplate,
      name: prompt(isTemplate ? "Template Name:" : "Writing File Name:") ?? "",
      organizationId,
    };
    if (selectedTemplateId) {
      const templateToUse = writingsTemplates?.find((wt) => Number(wt.id) === Number(selectedTemplateId));
      writingParams.bodyHtml = templateToUse?.body_html;
      writingParams.bodyText = templateToUse?.body_text;
    }
    writingCreate(writingParams);
  };

  // RENDER
  return (
    <div>
      <StyledWritingsBoxLead>
        <h2>{isTemplate ? "Templates" : "Writings"}</h2>
        <form onSubmit={onWritingCreate}>
          <select value={selectedTemplateId} onChange={(e) => setSelectedTemplateId(e.target.value)}>
            <option value="">--- Without Template ---</option>
            {writingsTemplates?.map((wt) => (
              <option key={wt.id} value={wt.id}>
                Template: {wt.name}
              </option>
            ))}
          </select>
          <button type="submit">+ {isTemplate ? "Template" : "Writing"}</button>
        </form>
      </StyledWritingsBoxLead>
      <StyledWritingsBox>
        {writings?.map((w) => (
          <div key={w.id} className="writings-box__writing">
            <p>
              <Link to={caseId ? `/case/${caseId}/writing/${w.id}` : `/writing/${w.id}`}>{w.name ?? "Untitled"}</Link>
            </p>
          </div>
        ))}
      </StyledWritingsBox>
    </div>
  );
};

const StyledWritingsBoxLead = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 12px;
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
  margin: 20px 12px;
  button {
    width: 100%;
  }
  .writings-box__writing {
    background: white;
    border-radius: 4px;
    padding: 8px 12px 8px;
    margin: 4px 0;
    display: flex;
    justify-content: space-between;
    &.processing {
      opacity: 0.5;
      text-align: center;
      margin-bottom: 6px;
      margin-top: 0;
    }
  }
`;
