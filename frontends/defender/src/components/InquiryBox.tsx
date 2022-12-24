import { orderBy } from "lodash";
import { ResetIcon } from "@radix-ui/react-icons";
import { useEffect } from "react";
import { useParams } from "react-router-dom";
import styled from "styled-components";
import { useAppStore } from "../data/AppStore";
import { useCases } from "../data/useCases";
import { DocumentContentLocationBox } from "./DocumentContentLocationBox";
import { CasePanel } from "./CasePanel";
import { useWritings } from "../data/useWritings";
import { WritingPanel } from "./WritingsBox";
import { useInquiryStore } from "../data/InquiryStore";

export const InquiryBox = () => {
  const app = useAppStore();
  const params = useParams(); // TODO: get from props, not params
  const { data: cases } = useCases({ organizationId: app.focusedOrgId });
  const { data: writings } = useWritings({ organizationId: app.focusedOrgId });

  const {
    inquiryScope,
    setInquiryScope,
    query,
    setQuery,
    answerQuestion,
    answerDetailsLocations,
    answerCaseFactsSimilarity,
    answerWritingSimilarity,
    isInquirySubmitted,
    inquiry,
    focusAnswer,
    setFocusAnswer,
    clearInquiry,
  } = useInquiryStore();

  // ON MOUNT
  // --- update scope to whatever vars available
  useEffect(() => {
    if (params?.documentId != null) {
      setInquiryScope("document");
    } else if (params.caseId != null) {
      setInquiryScope("case");
    } else {
      setInquiryScope("organization");
    }
  }, [params]);

  // RENDER
  return (
    <StyledInquiryBox>
      <form
        className="inquiry-box__input"
        onSubmit={(e) => {
          e.preventDefault();
          inquiry({ caseId: params.caseId, documentId: params.documentId, organizationId: app.focusedOrgId });
        }}
      >
        {/* @ts-ignore */}
        <select disabled={isInquirySubmitted} value={inquiryScope} onChange={(e) => setInquiryScope(e.target.value)}>
          <option value="caselaw" disabled>
            Case Law
          </option>
          <option value="organization">Organization</option>
          <option value="case" disabled={params.caseId == null}>
            Case
          </option>
          <option value="document" disabled={params.documentId == null}>
            Document
          </option>
        </select>
        <label>
          {/* <span>Ask Question</span> */}
          <input
            disabled={isInquirySubmitted}
            placeholder="Where did the search warrant authorize a raid on?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </label>
        <button type="submit" disabled={isInquirySubmitted || query.length < 4}>
          Ask AI
        </button>
      </form>

      {isInquirySubmitted && (
        <>
          <div className="inquiry-box__tabs">
            {answerDetailsLocations && (
              <label className={focusAnswer === "location" ? "active" : ""} onClick={() => setFocusAnswer("location")}>
                Detail Locations {answerDetailsLocations?.inProgress ? "(Loading...)" : ""}
              </label>
            )}
            {answerQuestion && (
              <label className={focusAnswer === "question" ? "active" : ""} onClick={() => setFocusAnswer("question")}>
                Answer/Summary {answerQuestion?.inProgress ? "(Loading...)" : ""}
              </label>
            )}
            {answerCaseFactsSimilarity && (
              <label
                className={focusAnswer === "caseFacts" ? "active" : ""}
                onClick={() => setFocusAnswer("caseFacts")}
              >
                Similar Case Facts {answerCaseFactsSimilarity?.inProgress ? "(Loading...)" : ""}
              </label>
            )}
            {answerWritingSimilarity && (
              <label
                className={focusAnswer === "writingSimilarity" ? "active" : ""}
                onClick={() => setFocusAnswer("writingSimilarity")}
              >
                Writings {answerWritingSimilarity?.inProgress ? "(Loading...)" : ""}
              </label>
            )}
            <label className="reset-inquiry-btn" onClick={clearInquiry}>
              <ResetIcon />
            </label>
          </div>
          <div className="inquiry-box__focus">
            {/* ANSWER */}
            {focusAnswer === "question" ? (
              <>
                <p>{answerQuestion?.answer}</p>
                <ul>
                  {orderBy(answerQuestion?.locations, ["score"], ["desc"])?.map((l) => (
                    <li key={l.document_content.id}>
                      <DocumentContentLocationBox location={l} />
                    </li>
                  ))}
                </ul>
              </>
            ) : null}
            {/* DETAILS */}
            {focusAnswer === "location" ? (
              <>
                <ul>
                  {orderBy(answerDetailsLocations?.locations, ["score"], ["desc"])?.map((l) => (
                    <li key={l.document_content.id}>
                      <DocumentContentLocationBox location={l} />
                    </li>
                  ))}
                </ul>
              </>
            ) : null}
            {/* CASE FACTS */}
            {focusAnswer === "caseFacts" ? (
              <>
                {orderBy(answerCaseFactsSimilarity?.locations, ["score"], ["desc"])?.map((l) => (
                  <CasePanel key={l.case_id} cse={cases?.find((c) => c.id === l.case_id)!} />
                ))}
              </>
            ) : null}
            {/* WRITING SIMILARITY */}
            {focusAnswer === "writingSimilarity" && writings ? (
              <>
                {orderBy(answerWritingSimilarity?.locations, ["score"], ["desc"])
                  ?.map((l) => writings.find((w) => w.id === l.writing_id))
                  ?.map((wr) => (
                    // @ts-ignore
                    <WritingPanel key={wr.id} writing={wr} />
                  ))}
              </>
            ) : null}
          </div>
        </>
      )}
    </StyledInquiryBox>
  );
};

const StyledInquiryBox = styled.div`
  display: flex;
  flex-direction: column;
  margin: -6px 12px 0 !important;
  background: white;
  padding: 12px;
  padding-top: 12px !important;
  margin-bottom: 12px;

  .inquiry-box__input {
    display: flex;
    width: 100%;
    label,
    input,
    select {
      width: 100%;
      display: flex;
      flex-grow: 1;
      align-items: center;
    }
    button,
    label > span {
      min-width: 120px;
      font-size: 12px;
    }
    & > select {
      max-width: 100px;
    }
  }
  .inquiry-box__tabs {
    padding: 4px 0;
    margin-top: 12px;
    display: flex;
    label {
      display: flex;
      align-items: center;
      justify-content: center;
      flex: 1;
      flex-grow: 1;
      text-align: center;
      padding: 4px 0;
      margin: 0 2px;
      border-bottom: 2px solid #eee;
      color: #aaa;
      cursor: pointer;
      font-size: 14px;
      background: #eee;
      &.active {
        border-bottom: 2px solid blue;
        background: blue;
        color: white;
      }
    }
  }
  .inquiry-box__focus {
    padding-top: 12px;
    font-size: 13px;
    ul {
      list-style-type: none;
      padding-left: 0;
    }
    li {
      margin-top: 4px;
    }
    b {
      font-weight: 700;
    }
  }
  .reset-inquiry-btn {
    width: 54px;
    max-width: 54px;
  }
`;
