import React, { useState } from "react";
import { Navigate, redirect } from "react-router-dom";
import { useUser, useUserLogin } from "../../data/useUser";

export const ViewLogin = () => {
  const { data: user } = useUser();
  const { mutateAsync: userLogin } = useUserLogin();
  const [loginEmail, setLoginEmail] = useState("gideon@gideon.com");
  const [loginPassword, setLoginPassword] = useState("gideon");
  const handleLogin = (e) => {
    e.preventDefault();
    userLogin({ email: loginEmail, password: loginPassword });
  };

  return (
    <div>
      {user && <Navigate to="/" replace={true} />}
      <form onSubmit={handleLogin}>
        <label>
          Email
          <input type="email" value={loginEmail} onChange={(e) => setLoginEmail(e.target.value)} />
        </label>
        <label>
          Password
          <input type="password" value={loginPassword} onChange={(e) => setLoginPassword(e.target.value)} />
        </label>
        <button type="submit">Login</button>
      </form>
    </div>
  );
};
