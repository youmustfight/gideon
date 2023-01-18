import React, { useEffect } from "react";
import { Navigate, Route, Routes } from "react-router";
import { ViewCase } from "./routes/case/ViewCase";
import { ViewLogin } from "./routes/login/ViewLogin";
import { useUser } from "../src/data/useUser";
import { ViewCases } from "./routes/cases/ViewCases";
import { Link } from "react-router-dom";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { ToolWindow } from "./components/ToolWindow";
import { ViewWritingPDF } from "./routes/writing/ViewWritingPDF";
import { ViewOrganizations } from "./routes/organizations/ViewOrganizations";
import { useOrganizations } from "./data/useOrganizations";
import { useAppStore } from "./data/AppStore";
import { ViewWriting } from "./routes/writing/ViewWriting";
import { ViewProfile } from "./routes/profile/ViewProfile";
import { ViewCaseLaw } from "./routes/caselaw/ViewCaseLaw";
import { AppHeader } from "./components/AppHeader";
import { ViewSandbox } from "./routes/sandbox/ViewSandbox";

export const Gideon: React.FC = () => {
  const { data: user, isSuccess: isSuccessUserFetch } = useUser();
  const { data: organizations } = useOrganizations();
  const { focusedOrgId, setFocusedOrgId } = useAppStore();
  // ON MOUNT
  useEffect(() => {
    // DEPRECATED: removed this bc we now have a 'playground' page a person can land at. Before we needed initial cases view to focus on
    // // --- set focused org if none
    // if (!focusedOrgId && organizations && user) {
    //   const userOrgId = organizations?.find((o) => o.users.some((u) => u.id === user.id))?.id;
    //   if (userOrgId) setFocusedOrgId(userOrgId);
    // }
  }, [organizations, user]);

  // RENDER
  return !isSuccessUserFetch ? null : (
    <Routes>
      {/* AUTH */}
      <Route
        path="/login"
        element={
          <ToolWindow>
            <ViewLogin />
          </ToolWindow>
        }
      />
      {/* ORGANIZATIONS */}
      <Route
        path="/organizations"
        element={
          <ProtectedRoute user={user}>
            <AppHeader />
            <ToolWindow>
              <ViewOrganizations />
            </ToolWindow>
          </ProtectedRoute>
        }
      />
      {/* PERSONAL VIEW AKA PLAYGROUND */}
      <Route
        path="/"
        element={
          <ProtectedRoute user={user}>
            <AppHeader />
            <ToolWindow maxWidth="720px">
              <ViewSandbox />
            </ToolWindow>
          </ProtectedRoute>
        }
      />
      {/* CASES */}
      <Route
        path="/cases"
        element={
          <ProtectedRoute user={user}>
            <AppHeader />
            <ToolWindow>
              <ViewCases />
            </ToolWindow>
          </ProtectedRoute>
        }
      />
      <Route
        path="/case/:caseId/*"
        element={
          <ProtectedRoute user={user}>
            <AppHeader />
            <ToolWindow>
              <ViewCase />
            </ToolWindow>
          </ProtectedRoute>
        }
      />
      <Route
        path="/caselaw/*"
        element={
          <ProtectedRoute user={user}>
            <AppHeader />
            <ToolWindow>
              <ViewCaseLaw />
            </ToolWindow>
          </ProtectedRoute>
        }
      />
      {/* WRITINGS */}
      <Route
        path="/writing/:writingId"
        element={
          <ProtectedRoute user={user}>
            <AppHeader />
            <ToolWindow>
              <ViewWriting />
            </ToolWindow>
          </ProtectedRoute>
        }
      />
      <Route
        path="/writing/:writingId/pdf"
        element={
          <ProtectedRoute user={user}>
            <ViewWritingPDF />
          </ProtectedRoute>
        }
      />
      {/* SETTINGS/PROFILE */}
      <Route
        path="/profile"
        element={
          <ProtectedRoute user={user}>
            <AppHeader />
            <ToolWindow>
              <ViewProfile />
            </ToolWindow>
          </ProtectedRoute>
        }
      />
      {/* NO MATCH */}
      <Route
        path="*"
        element={
          <ToolWindow>
            <div>
              Missing Page. Go to <Link to="/login">login</Link>.
            </div>
          </ToolWindow>
        }
      />
    </Routes>
  );
};
