import styled from "styled-components";

export const Button = styled.button`
  font-family: "GT Walsheim";
  margin: 0 2px;
  padding: 4px;
  border-radius: 0;
  border: 1px solid var(--color-blue-500);
  color: white;
  background: var(--color-blue-500);
  font-size: 12px;
  cursor: pointer;
  &:disabled {
    border: 1px solid var(--color-blue-800);
    background: var(--color-blue-800);
  }
`;
