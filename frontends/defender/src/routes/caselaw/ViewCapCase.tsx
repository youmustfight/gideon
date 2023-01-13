import { startCase } from "lodash";
import React, { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { Link } from "react-router-dom";
import { ConfirmButton } from "../../components/ConfirmButton";
import { StyledBodyTextBox } from "../../components/styled/StyledBodyTextBox";
import { reqCapCaseDelete, reqCapCaseExtractions, reqCapCaseIndex, useCapCase } from "../../data/useCapCase";

export const ViewCapCase = () => {
  const navigate = useNavigate();
  const capRef = useRef();
  const { capId } = useParams();
  const [isSummaryFullyVisible, setIsSummaryFullyVisible] = useState(false);
  const { data: capCase, refetch } = useCapCase(capId);
  // --- deletion
  const [isDeleting, setIsDeleting] = useState(false);
  const deleteHandler = async () => {
    setIsDeleting(true);
    await reqCapCaseDelete(Number(capId));
    navigate(`/caselaw`);
  };

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
  // @ts-ignore
  return !capCase ? (
    <div>
      <div className="section-lead title">
        <button onClick={() => reqCapCaseIndex(capId!).then(() => refetch())} style={{ flexGrow: "1" }}>
          Index Case
        </button>
      </div>
    </div>
  ) : (
    // @ts-ignore
    <div ref={capRef}>
      {/* TITLE */}
      <div className="section-lead title">
        <h2>
          {capCase.name} ({capCase.decision_date.slice(0, 4)})
        </h2>
      </div>

      {/* CASE BRIEF */}
      <div className="section-lead">
        <h3>Case Brief</h3>
      </div>
      <section>
        <div>
          <h4>Summary</h4>
        </div>
        <div>
          <p>
            {isSummaryFullyVisible ? capCase.generated_summary : capCase.generated_summary?.slice(0, 400)}{" "}
            <u onClick={() => setIsSummaryFullyVisible(!isSummaryFullyVisible)}>
              {isSummaryFullyVisible ? "...Hide more" : "...Show more"}
            </u>{" "}
          </p>
        </div>
        <br />
        <div style={{ display: "flex", width: "100%" }}>
          <button onClick={() => reqCapCaseExtractions(capId!)} style={{ flexGrow: "1" }}>
            Regenerate Summary
          </button>
        </div>
        {/* <div>
          <h4>Case Brief</h4>
        </div>
        <div>
          <p>TODO</p>
        </div> */}
      </section>

      {/* PARTIES */}
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

      {/* OPINIONS */}
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

      {/* CITATIONS */}
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

      {/* DELETES */}
      <hr />
      <section>
        <ConfirmButton
          prompts={["Delete Case Law", "Yes, Delete Case Law"]}
          onClick={deleteHandler}
          disabled={isDeleting}
          style={{ width: "100%" }}
        />
      </section>
    </div>
  );
};
