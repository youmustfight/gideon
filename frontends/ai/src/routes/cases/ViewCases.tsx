import React from "react";
import { Link } from "react-router-dom";
import { useCases } from "../../data/useCases";
import { useUser } from "../../data/useUser";

export const ViewCases = () => {
  const { data: user } = useUser();
  const { data: cases } = useCases({ userId: user?.id });

  return (
    <div>
      {cases?.map((c) => (
        <div key={c.id}>
          <Link to={`/case/${c.id}`}>Link to {c.id}</Link>
        </div>
      ))}
    </div>
  );
};
