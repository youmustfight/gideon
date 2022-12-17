import React, { useEffect } from "react";
import { Route, Routes, useNavigate } from "react-router";
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

export const Gideon: React.FC = () => {
  const navigate = useNavigate();
  const { data: user, isSuccess: isSuccessUserFetch } = useUser();
  const { data: organizations } = useOrganizations();
  const { focusedCaseId, focusedOrgId, setFocusedOrgId } = useAppStore();
  // ON MOUNT
  // --- set focused org if none
  useEffect(() => {
    if (!focusedOrgId && organizations?.[0]?.id) setFocusedOrgId(organizations?.[0]?.id);
  }, [organizations]);

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
            <ToolWindow>
              <ViewOrganizations />
            </ToolWindow>
          </ProtectedRoute>
        }
      />
      {/* CASES */}
      <Route
        path="/cases"
        element={
          <ProtectedRoute user={user}>
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
            <ToolWindow>
              <ViewCase />
            </ToolWindow>
          </ProtectedRoute>
        }
      />
      {/* WRITINGS */}
      <Route
        path="/writing/:writingId"
        element={
          <ProtectedRoute user={user}>
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
