import React from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { useAppStore } from "../data/AppStore";
import { useCaseCreate } from "../data/useCase";
import { useCases } from "../data/useCases";
import { useUser } from "../data/useUser";
import { CasePanel } from "./CasePanel";
import { Button } from "./styled/common/Button";

export const OrgCasesList: React.FC = () => {
  const navigate = useNavigate();
  const app = useAppStore();
  const { data: user } = useUser();
  const { data: cases } = useCases({ organizationId: app.focusedOrgId });
  const { mutateAsync: caseCreate } = useCaseCreate();
  // --- case creation post navigation
  const caseCreationHelper = async () => {
    if (user) {
      const cse = await caseCreate({
        name: prompt("Name of Case:") ?? "",
        organization_id: app.focusedOrgId,
        user_id: user.id,
      });
      navigate(`/case/${cse.id}`);
    }
  };

  // RENDER
  return (
    <StyledOrgCasesList>
      <div className="cases-driver__section-lead">
        <h2>Cases</h2>
        {user ? <Button onClick={() => caseCreationHelper()}>+ Add Case</Button> : null}
      </div>
      {cases && (
        <>
          {/* CASES LISTS */}
          {cases.map((c) => (
            <CasePanel key={c.id} cse={c} />
          ))}
        </>
      )}
    </StyledOrgCasesList>
  );
};

const StyledOrgCasesList = styled.div`
  .cases-driver__section-lead {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 4px;
    margin-bottom: 12px;
    padding: 4px;
    h2 {
      font-weight: 900;
      font-size: 20px;
    }
    button {
      width: 100px;
      min-width: 100px;
      max-width: 100px;
    }
  }
`;
