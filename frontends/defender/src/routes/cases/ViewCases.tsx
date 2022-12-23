import styled from "styled-components";
import { OrgCasesList } from "../../components/OrgCasesList";
import { OrganizationDriver } from "../../components/OrganizationDriver";
import { WritingsBox } from "../../components/WritingsBox";
import { useAppStore } from "../../data/AppStore";
import { useOrganizations } from "../../data/useOrganizations";

export const ViewCases = () => {
  const { data: organizations } = useOrganizations();
  const { focusedOrgId } = useAppStore();
  const focusedOrg = organizations?.find((o) => o.id === focusedOrgId);

  // RENDER
  return !organizations || !focusedOrgId ? null : (
    <StyledViewCases key={focusedOrgId}>
      <div className="view-cases__panels">
        {focusedOrg && <OrganizationDriver organization={focusedOrg} />}
        <OrgCasesList />
        <WritingsBox isTemplate organizationId={focusedOrgId} />
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
