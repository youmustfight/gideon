import React from "react";
import { Navigate, Route, Routes } from "react-router";
import styled from "styled-components";
import { ViewCase } from "./routes/case/ViewCase";
import { ViewLogin } from "./routes/login/ViewLogin";
import { useUser } from "../src/data/useUser";
import { ViewCases } from "./routes/cases/ViewCases";

export const Gideon: React.FC = () => {
  const { data: user } = useUser();
  // RENDER
  return (
    <>
      <Routes>
        {/* AUTH */}
        <Route path="/login" element={!user ? <ViewLogin /> : <Navigate to="/" />} />
        {/* CASES */}
        <Route path="/cases/*" element={user ? <ViewCases /> : <Navigate to="/" />} />
        {/* CASE */}
        <Route path="/case/*" element={user ? <ViewCase /> : <Navigate to="/" />} />
        {/* ELSE */}
        <Route path="*" element={user ? <Navigate to="/cases" /> : <Navigate to="/login" />} />
      </Routes>
    </>
  );
};
