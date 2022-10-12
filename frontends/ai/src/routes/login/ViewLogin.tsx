import React, { useState } from "react";
import { useUserLogin } from "../../data/useUser";

export const ViewLogin = () => {
  const { mutateAsync: userLogin } = useUserLogin();
  const [loginEmail, setLoginEmail] = useState("mark@gideon.com");
  const [loginPassword, setLoginPassword] = useState("");
  const handleLogin = (e) => {
    e.preventDefault();
    userLogin({ email: loginEmail, password: loginPassword });
  };

  return (
    <div>
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
