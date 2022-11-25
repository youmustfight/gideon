import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter } from "react-router-dom";
import { QueryClientProvider } from "react-query";
import { queryClient } from "./data/queryClient";
import { Gideon } from "./Gideon";
import { ResetCSS } from "./components/ResetCSS";

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ResetCSS />
        <Gideon />
      </BrowserRouter>
    </QueryClientProvider>
  );
};

ReactDOM.render(<App />, document.querySelector("#root"));
