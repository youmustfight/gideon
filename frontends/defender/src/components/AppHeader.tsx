import React from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { useAppStore } from "../data/AppStore";
import { useOrganizations } from "../data/useOrganizations";

export const AppHeader = () => {
  const navigate = useNavigate();
  const { focusedOrgId, setFocusedOrgId } = useAppStore();
  const { data: organizations } = useOrganizations();

  // RENDER
  return (
    <StyledAppHeader>
      <span
        onClick={() => {
          setFocusedOrgId(undefined);
          navigate("/");
        }}
      >
        <b>GIDEON</b>
      </span>
      <select
        value={focusedOrgId ?? ""}
        onChange={(e) => {
          if (e.target.value === "") {
            setFocusedOrgId(undefined);
            navigate("/");
          } else {
            setFocusedOrgId(Number(e.target.value));
            navigate("/cases");
          }
        }}
      >
        <option value="">Sandbox</option>
        <optgroup label="Organizations">
          {organizations?.map((o) => (
            <option key={o.id} value={o.id}>
              {o.name}
            </option>
          ))}
        </optgroup>
      </select>
      <span onClick={() => navigate("/profile")}>Profile</span>
    </StyledAppHeader>
  );
};

const StyledAppHeader = styled.header`
  display: flex;
  justify-content: space-between;
  background: var(--color-blue-900);
  padding: 16px 20px 10px;
  border-bottom: 2px solid var(--color-blue-850);
  font-size: 16px;
  font-family: "GT Walsheim";

  span,
  select {
    font-weight: 700;
    cursor: pointer;
    color: var(--color-blue-500);
  }

  select {
    border: none;
    outline: none;
    background: none;
    padding-bottom: 6px;
    border-bottom: 2px solid var(--color-blue-800);
  }
`;
