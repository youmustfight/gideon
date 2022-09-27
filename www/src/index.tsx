import React from "react";
import ReactDOM from "react-dom";
import { QueryClientProvider } from "react-query";
import { queryClient } from "./data/queryClient";
import { Gideon } from "./Gideon";

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Gideon />
    </QueryClientProvider>
  );
};

ReactDOM.render(<App />, document.querySelector("#root"));
