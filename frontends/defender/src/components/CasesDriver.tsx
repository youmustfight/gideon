import React from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { useCaseCreate } from "../data/useCase";
import { useCases } from "../data/useCases";
import { useUser } from "../data/useUser";

export const CasesDriver: React.FC = () => {
  const navigate = useNavigate();
  const { data: user } = useUser();
  const { data: cases } = useCases({ userId: user?.id });
  const { mutateAsync: caseCreate } = useCaseCreate();
  // --- case creation post navigation
  const caseCreationHelper = async () => {
    if (user) {
      const cse = await caseCreate({ userId: user.id });
      navigate(`/case/${cse.id}`);
    }
  };

  // RENDER
  return (
    <StyledCasesDriver>
      <div className="cases-driver__section-lead">
        <h2>Cases</h2>
        {user ? <button onClick={() => caseCreationHelper()}>+ Add Case</button> : null}
      </div>
      {cases?.map((c) => (
        <div key={c.id} className="cases-driver__case-box">
          <span>
            {c.name ?? "Untitled Case"} (#{c.id})
          </span>
          <button onClick={() => navigate(`/case/${c.id}`)}>➡</button>
        </div>
      ))}
    </StyledCasesDriver>
  );
};

const StyledCasesDriver = styled.div`
  .cases-driver__section-lead {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 24px 16px;
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
  .cases-driver__case-box {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: white;
    border-radius: 4px;
    margin: 12px;
    padding: 12px;
    border: 1px solid #ddd;
    transition: 250ms;
    &:hover {
      border: 1px solid blue;
    }
    button {
      color: blue;
    }
  }
`;
