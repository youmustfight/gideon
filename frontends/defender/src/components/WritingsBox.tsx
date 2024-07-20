import { useState } from "react";
import { Link } from "react-router-dom";
import styled from "styled-components";
import { TWritingCreateParams, useWritingCreate } from "../data/useWriting";
import { TWriting, useWritings } from "../data/useWritings";
import { useAIRequestStore } from "./AIRequest/AIRequestStore";
import { Button } from "./styled/common/Button";
import { Select } from "./styled/common/Select";
import { SlimBox } from "./styled/StyledBox";

export const WritingPanel: React.FC<{ writing: TWriting }> = ({ writing }) => {
  return (
    <StyledWritingPanel>
      <p>
        <Link to={writing.case_id ? `/case/${writing.case_id}/writing/${writing.id}` : `/writing/${writing.id}`}>
          {writing.is_template ? "[TEMPLATE] " : ""}
          {writing.name ?? "Untitled"}
        </Link>
      </p>
    </StyledWritingPanel>
  );
};

const StyledWritingPanel = styled(SlimBox)`
  border: 1px solid #eee;
  transition: 250ms;
  &:hover {
    border: 1px solid blue;
  }
`;

type TWritingsBoxProps = {
  caseId?: number;
  isTemplate: boolean;
  organizationId?: number;
};

export const WritingsBox: React.FC<TWritingsBoxProps> = ({ caseId, isTemplate, organizationId }) => {
  const { scrollToAIRequestBox, setAIRequestType } = useAIRequestStore();
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
          <Select value={selectedTemplateId} onChange={(e) => setSelectedTemplateId(e.target.value)}>
            <option value="">--- No Template ---</option>
            {writingsTemplates?.map((wt) => (
              <option key={wt.id} value={wt.id}>
                Template: {wt.name}
              </option>
            ))}
          </Select>
          <Button onClick={() => onWritingCreate(false)}>{isTemplate ? "+ Template" : "+ New"}</Button>
          {selectedTemplateId && (
            <Button
              onClick={() => {
                setAIRequestType("write");
                scrollToAIRequestBox();
              }}
            >
              + Draft with AI
            </Button>
          )}
        </div>
      </StyledWritingsBoxLead>
      {writings && (
        <StyledWritingsBox>
          {writings?.map((w: any) => (
            <WritingPanel key={w.id} writing={w} />
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

const StyledWritingsBox = styled.div`
  margin: 8px 4px 20px;
  button {
    width: 100%;
  }
`;
