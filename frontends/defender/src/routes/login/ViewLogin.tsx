import React, { useState } from "react";
import { Navigate, redirect } from "react-router-dom";
import styled from "styled-components";
import { Button } from "../../components/styled/common/Button";
import { Input } from "../../components/styled/common/Input";
import { H3, Label } from "../../components/styled/common/Typography";
import { useUser, useUserLogin } from "../../data/useUser";

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
      {user && <Navigate to="/" replace={true} />}
      <StyledViewLogin>
        <div className="login-wrapper">
          <H3>Login</H3>
          <form onSubmit={handleLogin}>
            <Label htmlFor="login-email">Email</Label>
            <Input id="login-email" type="email" value={loginEmail} onChange={(e) => setLoginEmail(e.target.value)} />
            <Label htmlFor="login-password">Password</Label>
            <Input
              id="login-password"
              type="password"
              value={loginPassword}
              onChange={(e) => setLoginPassword(e.target.value)}
            />
            <Button type="submit">Login</Button>
            {loginError && <div className="login-error">{loginError}</div>}
          </form>
        </div>
      </StyledViewLogin>
    </>
  );
};

const StyledViewLogin = styled.div`
  min-height: 80vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  .login-wrapper {
    width: 100%;
    max-width: 400px;
    margin: 0 auto;
    padding: 24px;
    background: white;
    box-shadow: var(--effects-box-shadow-500);
    input {
      margin-bottom: 12px;
      width: 100%;
    }
    button {
      width: 100%;
    }
    h3 {
      font-weight: 900;
      margin-bottom: 12px;
      padding-bottom: 6px;
      color: var(--color-blue-500);
      border-bottom: 2px solid var(--color-blue-500);
    }
    label {
      font-size: 13px;
    }
    input {
      margin-top: 4px;
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
