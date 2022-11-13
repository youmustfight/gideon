import React from "react";
import { Navigate, Route, Routes } from "react-router";
import styled from "styled-components";
import { ViewCase } from "./routes/case/ViewCase";
import { ViewLogin } from "./routes/login/ViewLogin";
import { useUser } from "../src/data/useUser";
import { ViewCases } from "./routes/cases/ViewCases";
import { Link } from "react-router-dom";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { ToolWindow } from "./components/ToolWindow";

export const Gideon: React.FC = () => {
  const { data: user, isSuccess: isSuccessUserFetch } = useUser();

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
      {/* CASE */}
      <Route
        path="/case/*"
        element={
          <ProtectedRoute user={user}>
            <ToolWindow>
              <ViewCase />
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
