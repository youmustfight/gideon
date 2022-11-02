import React from "react";
import { Navigate, Route, Routes } from "react-router";
import styled from "styled-components";
import { ViewCase } from "./routes/case/ViewCase";
import { ViewLogin } from "./routes/login/ViewLogin";
import { useUser } from "../src/data/useUser";
import { ViewCases } from "./routes/cases/ViewCases";
import { Link } from "react-router-dom";
import { ProtectedRoute } from "./components/ProtectedRoute";

export const Gideon: React.FC = () => {
  const { data: user } = useUser();
  // RENDER
  return (
    <>
      <Routes>
        {/* CASES */}
        <Route
          path="/"
          element={
            <ProtectedRoute user={user}>
              <ViewCases />
            </ProtectedRoute>
          }
        />

        {/* CASE */}
        <Route
          path="/case/*"
          element={
            <ProtectedRoute user={user}>
              <ViewCase />
            </ProtectedRoute>
          }
        />

        {/* AUTH */}
        <Route path="/login" element={<ViewLogin />} />

        {/* NO MATCH */}
        {/* React Router V6 removes <Switch/> and says don't do navigates in <Routes/>  */}
        {/* <Route path="/" element={user ? <Navigate to="/cases" /> : <Navigate to="/login" />} /> */}
        <Route
          path="*"
          element={
            <div>
              Missing Page. Go to <Link to="/login">login</Link>.
            </div>
          }
        />
      </Routes>
    </>
  );
};
