import { useNavigate } from "react-router";
import styled from "styled-components";
import { CasesDriver } from "../../components/CasesDriver";
import { OrganizationPanel } from "../../components/OrganizationPanel";
import { WritingsBox } from "../../components/WritingsBox";
import { useAppStore } from "../../data/AppStore";
import { useOrganizations } from "../../data/useOrganizations";
import { useUserLogout } from "../../data/useUser";

export const ViewCases = () => {
  const navigate = useNavigate();
  const { mutateAsync: logout } = useUserLogout();
  const { data: organizations } = useOrganizations();
  const { focusedOrgId } = useAppStore();

  // RENDER
  return !organizations || !focusedOrgId ? null : (
    <StyledViewCases key={focusedOrgId}>
      <div className="view-cases__panels">
        <OrganizationPanel organization={organizations?.find((o) => o.id === focusedOrgId)} />
        <CasesDriver />
        <WritingsBox isTemplate organizationId={focusedOrgId} />
      </div>
      <div className="view-cases__buttons">
        <button onClick={() => navigate("/organizations")}>Go to Organizations</button>
        <button onClick={() => logout()}>Logout</button>
      </div>
    </StyledViewCases>
  );
};

const StyledViewCases = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 100vh;
  .view-cases__panels {
    & > * {
      padding: 12px;
    }
  }
  .view-cases__buttons {
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding-bottom: 8px;
    button {
      margin: 4px 20px;
      cursor: pointer;
    }
  }
`;
