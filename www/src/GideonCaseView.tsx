import React from "react";
import { DiscoveryBox } from "./components/DiscoveryBox";
import { useDocuments } from "./data/useDocuments";

export const GideonCaseView = () => {
  return (
    <div>
      {/* DISCOVERY/INDEXED DOCS + UPLOAD */}
      <div className="section-lead">
        <h4>Discovery, Evidence, Exhibits</h4>
      </div>
      <section>
        <DiscoveryBox />
      </section>
    </div>
  );
};
