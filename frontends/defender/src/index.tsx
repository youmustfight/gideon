import React, { StrictMode } from "react";
import ReactDOM from "react-dom";
import { BrowserRouter } from "react-router-dom";
import { QueryClientProvider } from "react-query";
import { queryClient } from "./data/queryClient";
import { Gideon } from "./Gideon";
import { GlobalCSS } from "./components/styled/GlobalCSS";
import { ResetCSS } from "./components/styled/ResetCSS";
import "./data/axiosConfig";

const App: React.FC = () => {
  return (
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ResetCSS />
          <GlobalCSS />
          <Gideon />
        </BrowserRouter>
      </QueryClientProvider>
    </StrictMode>
  );
};

ReactDOM.render(<App />, document.querySelector("#root"));
