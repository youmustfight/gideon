import React, { useState } from "react";
import { Navigate, redirect } from "react-router-dom";
import styled from "styled-components";
import { useUser } from "../../data/useUser";
import { useUserLogin } from "../../data/useUserLogin";

export const ViewLogin = () => {
  const { data: user } = useUser();
  const { mutateAsync: userLogin } = useUserLogin();
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  // @ts-ignore
  const handleLogin = (e) => {
    e.preventDefault();
    userLogin({ email: loginEmail, password: loginPassword });
  };

  return (
    <>
      {user && <Navigate to="/cases" replace={true} />}
      <StyledViewLogin>
        <form onSubmit={handleLogin}>
          <label htmlFor="login-email">Email</label>
          <input id="login-email" type="email" value={loginEmail} onChange={(e) => setLoginEmail(e.target.value)} />
          <label htmlFor="login-password">Password</label>
          <input
            id="login-password"
            type="password"
            value={loginPassword}
            onChange={(e) => setLoginPassword(e.target.value)}
          />
          <button type="submit">Login</button>
        </form>
      </StyledViewLogin>
    </>
  );
};

const StyledViewLogin = styled.div`
  form {
    width: 100%;
    max-width: 240px;
    height: 400px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin: 0 auto;
    input {
      margin-bottom: 12px;
      width: 100%;
    }
    button {
      width: 100%;
    }
  }
`;
