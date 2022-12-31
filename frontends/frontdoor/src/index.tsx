import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter } from "react-router-dom";
import { Gideon } from "./Gideon";
import { ResetCSS } from "./components/ResetCSS";
import { GlobalCSS } from "./components/GlobalCSS";

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <ResetCSS />
      <GlobalCSS />
      <Gideon />
    </BrowserRouter>
  );
};

ReactDOM.render(<App />, document.querySelector("#root"));
