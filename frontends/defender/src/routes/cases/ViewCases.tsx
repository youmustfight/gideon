import styled from "styled-components";
import { CaseDriver } from "../../components/CaseDriver";
import { useUserLogout } from "../../data/useUserLogout";

export const ViewCases = () => {
  const { mutateAsync: logout } = useUserLogout();

  return (
    <StyledViewCases>
      <CaseDriver />
      <button onClick={() => logout()}>Logout</button>
    </StyledViewCases>
  );
};

const StyledViewCases = styled.div`
  display: flex;
  flex-direction: column;
  & > button {
    margin: 12px;
    background: transparent;
    border: none;
  }
`;
