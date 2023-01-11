import styled from "styled-components";

export const StyledAIRequestBoxTabs = styled.div`
  padding: 4px 0;
  display: flex;
  label {
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 1;
    flex-grow: 1;
    text-align: center;
    padding: 4px 0;
    margin: 0 2px;
    border-bottom: 2px solid #eee;
    color: #aaa;
    cursor: pointer;
    font-size: 14px;
    background: #eee;
    &.active {
      border-bottom: 2px solid blue;
      background: blue;
      color: white;
    }
  }
`;
