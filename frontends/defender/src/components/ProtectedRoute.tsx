import React from "react";
import { Navigate, Outlet } from "react-router";

export const ProtectedRoute = ({ user, redirectPath = "/login", children }: any) => {
  if (!user) {
    return <Navigate to={redirectPath} replace />;
  }
  return children ? children : <Outlet />;
};
