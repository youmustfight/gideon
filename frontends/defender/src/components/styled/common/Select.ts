import styled from "styled-components";

export const Select = styled.select`
  font-family: "GT Walsheim";
  padding: 8px;
  border-radius: 0;
  border: 1px solid var(--color-black-700);
  font-size: 14px;
  &:disabled {
    border: 1px solid var(--color-black-800);
    background: var(--color-black-900);
    color: var(--color-black-700);
  }
`;
