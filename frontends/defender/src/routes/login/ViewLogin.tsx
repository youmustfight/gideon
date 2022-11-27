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
  const [loginError, setLoginError] = useState(null);
  // @ts-ignore
  const handleLogin = (e) => {
    e.preventDefault();
    userLogin({ email: loginEmail, password: loginPassword }).catch((err) => {
      setLoginError(err);
    });
  };

  return (
    <>
      {user && <Navigate to="/cases" replace={true} />}
      <StyledViewLogin>
        <div className="login-wrapper">
          <h1>Gideon Login</h1>
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
            {loginError && <div className="login-error">{loginError}</div>}
          </form>
          <br />
          <p>
            Welcome Justin, Elliot, Eugeue, and others! Login above or{" "}
            <a href="https://youtu.be/M2tMmsGhp6c" target="_blank" rel="noreferer noopener">
              click here to see an old demo
            </a>
            .
          </p>
        </div>
      </StyledViewLogin>
    </>
  );
};

const StyledViewLogin = styled.div`
  .login-wrapper {
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
    h1 {
      font-weight: 900;
      margin-bottom: 12px;
      padding-bottom: 6px;
      border-bottom: 2px solid #ddd;
    }
    label {
      font-size: 13px;
    }
    p {
      font-size: 13px;
    }
    hr {
      width: 100%;
      margin: 20px 0;
      opacity: 0.5;
    }
  }
  .login-error {
    font-size: 12px;
    text-align: center;
    margin: 8px 4px 0;
  }
`;
