import React, { useEffect, useState } from "react";
import { useMatch, useNavigate } from "react-router";
import styled from "styled-components";
import { useCase } from "../data/useCase";
import { useCases } from "../data/useCases";
import { useCaseCreate } from "../data/useCaseCreate";
import { useCaseUpdate } from "../data/useCaseUpdate";
import { useUser } from "../data/useUser";

export const CaseDriver: React.FC = () => {
  const navigate = useNavigate();
  const matches = useMatch("/case/:caseId/*");
  const caseId = matches?.params?.caseId;
  const { data: user } = useUser();
  const { data: cse } = useCase(caseId);
  const { data: cases } = useCases({ userId: user?.id });
  const { mutateAsync: caseUpdate } = useCaseUpdate();
  const { mutateAsync: caseCreate } = useCaseCreate();
  // --- cases selecting
  const [selectedCaseNumber, setSelectedCaseNumber] = useState(caseId);
  const selectCaseHandler = (id: string) => {
    if (!id) {
      setSelectedCaseNumber("");
      navigate(`/cases`);
    } else {
      setSelectedCaseNumber(id);
      navigate(`/case/${id}`);
    }
  };
  // --- case creation post navigation
  const caseCreationHelper = async () => {
    if (user) {
      const cse = await caseCreate({ userId: user.id });
      navigate(`/case/${cse.id}`);
    }
  };

  // RENDER
  return (
    <StyledCaseDriver isViewingCase={cse != null}>
      {cse ? (
        <>
          <div>
            <button onClick={() => navigate("/cases")}>⬅</button>
            <label htmlFor="case-selector">Cases</label>
            <input value={cse.name} onChange={(e) => caseUpdate({ id: cse.id, name: e.target.value })} />
          </div>
        </>
      ) : (
        <div>
          <label htmlFor="case-selector">Go to Case</label>
          <select id="case-selector" value={selectedCaseNumber} onChange={(e) => selectCaseHandler(e.target.value)}>
            <option value="">--- Select Case ---</option>
            {cases?.map((c) => (
              <option key={c.id} value={String(c.id)}>
                {c.id} {c.name ? ` -- ${c.name}` : ""}
              </option>
            ))}
          </select>
          {user ? <button onClick={() => caseCreationHelper()}>+ Add Case</button> : null}
        </div>
      )}
    </StyledCaseDriver>
  );
};

const StyledCaseDriver = styled.div<{ isViewingCase: boolean }>`
  background: white;
  border-radius: 4px;
  margin: 12px;
  // margin-top: ${({ isViewingCase }) => (isViewingCase ? "0" : "24px")};
  padding: 12px;
  select {
    width: 100%;
  }
  & > div {
    display: flex;
    align-items: center;
    button {
      margin: 0 4px;
      white-space: pre;
    }
    label {
      margin-right: 8px;
      font-size: 13px;
      width: 80px;
      min-width: 80px;
      max-width: 80px;
    }
    input,
    select {
      width: 100%;
    }
  }
`;
