import { startCase } from "lodash";
import React, { useEffect, useRef } from "react";
import { useParams } from "react-router";
import { Link } from "react-router-dom";
import { StyledBodyTextBox } from "../../components/styled/StyledBodyTextBox";
import { useCapCase } from "../../data/useCapCase";

export const ViewCapCase = () => {
  const capRef = useRef();
  const { capId } = useParams();
  const { data: capCase } = useCapCase(capId);
  // ON MOUNT
  useEffect(() => {
    // --- scroll to CAP case viewer
    // @ts-ignore
    if (capId && capCase && capRef) {
      // @ts-ignore
      window.scrollTo(0, capRef.current.offsetTop);
    }
  }, [capId, capCase, capRef]);

  // RENDER
  console.log(capCase);
  // @ts-ignore
  return !capCase ? (
    <div>
      <div className="section-lead title">
        <h3>Loading...</h3>
      </div>
    </div>
  ) : (
    <div ref={capRef}>
      <div className="section-lead title">
        <h2>
          {capCase.name} ({capCase.decision_date.slice(0, 4)})
        </h2>
      </div>
      <div className="section-lead">
        <h3>Plaintiffs, Judges, Court</h3>
      </div>
      <section>
        <h4>
          <u>Jurisdiction / Court</u>
        </h4>
        <div>
          <p>
            {capCase.jurisdiction.name_long} / {capCase.court.name_abbreviation}
          </p>
        </div>
        <h4>
          <u>Parties</u>
        </h4>
        <div>
          {capCase.casebody.parties.map((p, pIndex) => (
            <p key={pIndex}>{p}</p>
          ))}
        </div>
        <h4>
          <u>Attorneys</u>
        </h4>
        <div>
          {capCase.casebody.attorneys.map((a, aIndex) => (
            <p key={aIndex}>{a}</p>
          ))}
        </div>
        <h4>
          <u>Docket</u>
        </h4>
        <div>
          <p>{capCase.docket_number}</p>
        </div>
        <h4>
          <u>Decision Date</u>
        </h4>
        <div>
          <p>{capCase.decision_date}</p>
        </div>
      </section>
      <div className="section-lead">
        <h4>Opinions</h4>
      </div>
      <section>
        <StyledBodyTextBox>
          {capCase.casebody.opinions.map((opinion, opinionIndex) => (
            <div key={`text-batch-${opinionIndex}`}>
              <div className="body-text__header">
                <h6>
                  {startCase(opinion.type)} Opinion: {opinion.author}
                </h6>
                <hr />
              </div>
              {opinion.text.split("\n").map((t, tIndex) => (
                <p key={tIndex}>{t}</p>
              ))}
            </div>
          ))}
        </StyledBodyTextBox>
      </section>
      <div className="section-lead">
        <h4>Citations</h4>
      </div>
      <section>
        <p>
          {capCase.cites_to.map((citation, citationIndex) => (
            <span key={[citation.cite, citationIndex].join("-")}>
              {citation.case_ids?.[0] ? (
                <Link to={`/caselaw/cap/${citation.case_ids?.[0]}`}>
                  {citation.reporter}, {citation.cite}
                </Link>
              ) : (
                `${citation.reporter}, ${citation.cite}`
              )}{" "}
            </span>
          ))}
        </p>
      </section>
    </div>
  );
};
