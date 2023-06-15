import styled from "styled-components";

export const Input = styled.input`
  font-family: "GT Walsheim";
  padding: 4px;
  border-radius: 0;
  border: 1px solid var(--color-black-700);
  font-size: 12px;
  color: var(--color-black-200);
  &:disabled {
    border: 1px solid var(--color-black-800);
    background: var(--color-black-900);
    color: var(--color-black-700);
  }
`;

export const TextArea = styled.textarea`
  font-family: "GT Walsheim";
  padding: 4px;
  border-radius: 0;
  border: 1px solid var(--color-black-700);
  font-size: 12px;
  color: var(--color-black-200);
  &:disabled {
    border: 1px solid var(--color-black-800);
    background: var(--color-black-900);
    color: var(--color-black-700);
  }
`;
