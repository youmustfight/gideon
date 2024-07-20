import styled from "styled-components";

export const StyledViewCase = styled.div`
  margin-top: 20px;
  a,
  a:active a:visited,
  a:hover {
    color: blue !important;
    text-decoration: none;
  }
  a:hover {
    text-decoration: underline;
  }
  section {
    box-shadow: rgb(0 0 0 / 4%) 0px 0 60px 0px;
    border-radius: 4px;
    padding: 12px;
    margin: 10px 12px;
    font-size: 13px;
    line-height: 115%;
    u {
      cursor: pointer;
    }
    h2,
    h4,
    h6 {
      font-weight: 900;
    }
    p {
      margin-bottom: 3px;
      margin-top: 3px;
    }
    ul {
      list-style-type: disc;
      padding-left: 12px;
      li {
        font-size: 13px;
        margin: 3px 0;
      }
    }
    &.no-shadow {
      box-shadow: none;
    }
    &:first-of-type {
      margin-top: 0;
    }
    &:last-of-type {
      margin-bottom: 0;
    }
  }
  .section-lead {
    display: flex;
    flex-direction: column;
    text-align: left;
    padding: 0 16px;
    margin: 4px 20px;
    h2 {
      font-size: 20px;
      font-weight: 900;
      margin: 6px 0;
    }
    h3,
    h4 {
      font-weight: 900;
      margin: 6px 0;
      display: flex;
      color: var(--color-black-500);
    }
    h2,
    h3,
    h4 {
      justify-content: center;
    }
    &.title {
      margin-top: 20px;
      margin-bottom: 20px;
      h2,
      h3 {
        font-size: 22px;
        text-align: center;
      }
    }
  }
  .document-header {
    margin: 12px 12px 0;
    padding: 20px 24px;
    background: #fff;
    border-radius: 4px;
    border-bottom: 2px solid #eee;
    display: flex;
    flex-direction: column;
    margin-bottom: 24px;
    .document-header__title {
      display: flex;
      margin-bottom: 12px;
      & > input {
        flex-grow: 1;
        height: 40px;
        font-size: 14px;
        font-weight: 700;
        text-align: center;
        &:disabled {
          color: initial;
        }
      }
      & > button {
        width: 150px;
        min-width: 150px;
        max-width: 150px;
      }
      & > a {
        display: none;
      }
      &:hover {
        & > a {
          display: flex;
          max-width: 40px;
          height: 100%;
          button {
            height: 40px;
            background: transparent;
            border: transparent;
            color: gray;
          }
        }
      }
    }
  }
`;
