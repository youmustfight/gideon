import styled from "styled-components";

export const BoxWithRightSideButton = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  border-radius: 4px;
  margin: 4px 12px;
  padding: 12px;
  border: 1px solid #ddd;
  transition: 250ms;
  &:hover {
    border: 1px solid blue;
  }
  button {
    color: blue;
  }
`;

export const SlimBox = styled.div`
  background: white;
  border-radius: 4px;
  padding: 8px 12px 8px;
  margin: 4px 0;
  display: flex;
  justify-content: space-between;
  &.processing {
    opacity: 0.5;
    text-align: center;
    margin-bottom: 6px;
    margin-top: 0;
  }
`;
