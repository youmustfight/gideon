import styled from "styled-components";
import { CasesDriver } from "../../components/CasesDriver";
import { useUserLogout } from "../../data/useUserLogout";

export const ViewCases = () => {
  const { mutateAsync: logout } = useUserLogout();

  return (
    <StyledViewCases>
      <CasesDriver />
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
