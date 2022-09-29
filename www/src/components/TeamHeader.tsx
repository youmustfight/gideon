import React from "react";
import styled from "styled-components";
import { useTeamStore } from "../data/TeamStore";

export const TeamHeader = () => {
  const { currentUser, setCurrentUser, users } = useTeamStore();

  return (
    <StyledTeamHeader>
      <span className="team-header__case-team">Case Team: </span>
      {users.map((u) => (
        <span key={u} className={`team-member ${u === currentUser ? "active" : ""}`} onClick={() => setCurrentUser(u)}>
          {u}
        </span>
      ))}
    </StyledTeamHeader>
  );
};

const StyledTeamHeader = styled.div`
  background: black;
  text-align: center;
  padding: 6px 4px;
  .team-header__case-team {
    color: white;
    font-size: 10px;
    border: none;
  }
  span.team-member {
    margin: 0 4px;
    border-radius: 12px;
    padding: 0px 4px;
    font-size: 13px;
    cursor: pointer;
    border: 1px solid white;
    color: white;
    &.active {
      background: white;
      color: black;
    }
  }
`;
