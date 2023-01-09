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
        <b>Gideon</b>
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
        style={{ border: "none" }}
      >
        <option value="">Playground</option>
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
  padding: 12px;
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  span {
    font-weight: 900;
    cursor: pointer;
  }
`;
