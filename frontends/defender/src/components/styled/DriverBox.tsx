import styled from "styled-components";

export const Styledriver = styled.div`
  background: white;
  border-radius: 4px;
  margin: 12px;
  padding: 0;
  & > div {
    padding: 12px 0;
  }
  .driver__lead {
    display: flex;
    align-items: center;
    button {
      margin: 0 12px;
    }
    .driver__lead__text {
      width: 100%;
      display: flex;
      button {
        position: relative;
        left: -54px;
      }
      & > *:not(button) {
        margin-left: -40px;
        margin-right: 12px;
      }
      input,
      h2 {
        width: auto;
        flex-grow: 1;
        font-size: 16px;
        padding: 4px;
        font-weight: 700;
      }
    }
  }
  .driver__toggle-details {
    font-size: 12px;
    opacity: 0.5;
    cursor: pointer;
    padding: 0 12px 12px;
    display: flex;
    justify-content: space-between;
  }
  .driver__details {
    padding: 0 12px 12px;
    table,
    thead,
    tbody {
      width: 100%;
      text-align: left;
    }
    table {
      margin: 0;
    }
    th,
    td,
    button {
      font-size: 13px;
    }
    th {
      font-weight: 900;
    }
    td select,
    td input {
      width: 100%;
    }
    td button {
      width: 100%;
    }
  }
`;
