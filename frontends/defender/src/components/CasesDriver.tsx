import React, { useState } from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { useAppStore } from "../data/AppStore";
import { TCase, useCaseCreate } from "../data/useCase";
import { useCases } from "../data/useCases";
import { reqQueryLegalBriefFactSimilarity } from "../data/useQueryAI";
import { useUser } from "../data/useUser";
import { BoxWithRightSideButton } from "./styled/StyledBox";

export const CasesDriver: React.FC = () => {
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
  // --- cases similarity
  const [similarComparisonCaseId, setSimilarComparisonCaseId] = useState<Number>();
  const [similarCaseIds, setSimilarCaseIds] = useState<Number[]>();
  const viewSimilarCasesHandler = async (caseId: number) => {
    setSimilarComparisonCaseId(caseId);
    const locations = await reqQueryLegalBriefFactSimilarity({ caseId }).then(({ locations }) => locations);
    // @ts-ignore
    setSimilarCaseIds(locations?.map((l) => l.case_id));
  };
  const clearSimilarCasesView = () => {
    setSimilarComparisonCaseId(undefined);
    setSimilarCaseIds(undefined);
  };

  // RENDER
  return (
    <StyledCasesDriver>
      <div className="cases-driver__section-lead">
        <h2>Cases</h2>
        {user ? <button onClick={() => caseCreationHelper()}>+ Add Case</button> : null}
      </div>
      {cases && (
        <>
          {/* CASES LISTS */}
          {similarComparisonCaseId ? (
            <>
              {/* SIMILARITY LIST */}
              {((c: any) => (
                <BoxWithRightSideButton>
                  <span>{c.name ?? "Untitled Case"}</span>
                  <div>
                    <button onClick={() => navigate(`/case/${c.id}`)}>➡</button>
                  </div>
                </BoxWithRightSideButton>
              ))(cases.find((c) => c.id === similarComparisonCaseId))}
              <button onClick={clearSimilarCasesView} style={{ width: "100%" }}>
                Clear Case Similarity Search
              </button>
              <hr />
              {similarCaseIds
                ? similarCaseIds
                    .map((caseId) => cases.find((c) => c.id === caseId))
                    .filter((c) => c != null)
                    .map((c: any) => (
                      <BoxWithRightSideButton key={c.id}>
                        <span>
                          {c.name ?? "Untitled Case"} (#{c.id})
                          <small className="case-panel__users">
                            <span className="case-panel__users__assigned">👩‍💼:</span>{" "}
                            {c.users?.map((u) => u.name).join(", ")}
                          </small>
                        </span>
                        <div>
                          <button onClick={() => navigate(`/case/${c.id}`)}>➡</button>
                        </div>
                      </BoxWithRightSideButton>
                    ))
                : null}
            </>
          ) : (
            <>
              {/* REGULAR CASES LIST */}
              {cases.map((c) => (
                <BoxWithRightSideButton key={c.id}>
                  <span>
                    {c.name ?? "Untitled Case"} (#{c.id})
                    <small className="case-panel__users">
                      <span className="case-panel__users__assigned">👩‍💼:</span> {c.users?.map((u) => u.name).join(", ")}
                    </small>
                  </span>
                  <div>
                    <button onClick={() => viewSimilarCasesHandler(c.id)}>View Cases Like This</button>
                    &ensp;
                    <button onClick={() => navigate(`/case/${c.id}`)}>➡</button>
                  </div>
                </BoxWithRightSideButton>
              ))}
            </>
          )}
        </>
      )}
    </StyledCasesDriver>
  );
};

const StyledCasesDriver = styled.div`
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
  .case-panel__users {
    display: block;
    margin-top: 4px;
    font-size: 12px;
  }
  .case-panel__users__assigned {
  }
`;
