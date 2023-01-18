import styled from "styled-components";

export const StyledBodyTextBox = styled.div`
  & > div {
    margin: 8px 0;
    padding: 8px;
    border-radius: 4px;
    .active {
      background: #ffffcf;
    }
    h6 {
      margin-bottom: 8px;
      text-deocration: underline;
      font-style: italic;
      font-size: 12px;
    }
    p {
      font-size: 14px;
    }
    .body-text__header {
      display: flex;
      align-items: center;
      hr {
        flex-grow: 1;
      }
    }
  }
`;
