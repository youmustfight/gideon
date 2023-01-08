import { orderBy } from "lodash";
import { ResetIcon } from "@radix-ui/react-icons";
import { useEffect } from "react";
import { useParams } from "react-router-dom";
import styled from "styled-components";
import { useAppStore } from "../../data/AppStore";
import { useCases } from "../../data/useCases";
import { DocumentContentLocationBox } from "../DocumentContentLocationBox";
import { CasePanel } from "../CasePanel";
import { useWritings } from "../../data/useWritings";
import { WritingPanel } from "../WritingsBox";
import { useAIRequestStore } from "./AIRequestStore";
import { CapCasePanel } from "../CapCasePanel";
import { AIRequestTypeSelect } from "./AIRequestBox";

type TInquiryBoxProps = {
  isCaseLawSearch?: boolean;
};

export const InquiryBox: React.FC<TInquiryBoxProps> = ({ isCaseLawSearch }) => {
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
    answerCaselaw,
    isAIRequestSubmitted,
    inquiry,
    focusAnswer,
    setFocusAnswer,
    clearInquiry,
  } = useAIRequestStore();

  // ON MOUNT
  // --- set initial search scope depending on vars available
  useEffect(() => {
    if (params?.documentId != null) {
      setInquiryScope("document");
    } else if (params.caseId != null) {
      setInquiryScope("case");
    } else if (isCaseLawSearch) {
      setInquiryScope("caselaw");
    } else {
      setInquiryScope("organization");
    }
  }, [params]);

  // RENDER
  return (
    <StyledInquiryBox>
      <form
        className="ai-request-box__input"
        onSubmit={(e) => {
          e.preventDefault();
          inquiry({ caseId: params.caseId, documentId: params.documentId, organizationId: app.focusedOrgId });
        }}
      >
        {/* Doing this inline bc we don't want to take up width on responses */}
        <AIRequestTypeSelect disabled={isAIRequestSubmitted} />
        {/* @ts-ignore */}
        <select
          disabled={isAIRequestSubmitted}
          value={inquiryScope}
          onChange={(e) => {
            const value = e.target.value;
            if (value === "caselaw") {
              window.open("/caselaw");
            } else {
              // @ts-ignore
              setInquiryScope(value);
            }
          }}
        >
          <option value="caselaw">Case Law</option>
          <option value="organization" disabled={isCaseLawSearch}>
            Organization
          </option>
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
            disabled={isAIRequestSubmitted}
            placeholder={(() => {
              if (isCaseLawSearch) return "Ex) Gideon v. Wainwright";
              if (inquiryScope === "organization") return "Ex) Cases involving Syrian refugees";
              return "Ex) What address was the search warrant for?";
            })()}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </label>
        <button type="submit" disabled={isAIRequestSubmitted || query.length < 4}>
          Run AI
        </button>
      </form>

      {isAIRequestSubmitted && (
        <>
          <div className="ai-request-box__tabs">
            {answerDetailsLocations && (
              <label className={focusAnswer === "location" ? "active" : ""} onClick={() => setFocusAnswer("location")}>
                Detail Locations {answerDetailsLocations?.inProgress ? "(Processing...)" : ""}
              </label>
            )}
            {answerQuestion && (
              <label className={focusAnswer === "question" ? "active" : ""} onClick={() => setFocusAnswer("question")}>
                Answer/Summary {answerQuestion?.inProgress ? "(Processing...)" : ""}
              </label>
            )}
            {answerCaseFactsSimilarity && (
              <label
                className={focusAnswer === "caseFacts" ? "active" : ""}
                onClick={() => setFocusAnswer("caseFacts")}
              >
                Similar Case Facts {answerCaseFactsSimilarity?.inProgress ? "(Processing...)" : ""}
              </label>
            )}
            {answerWritingSimilarity && (
              <label
                className={focusAnswer === "writingSimilarity" ? "active" : ""}
                onClick={() => setFocusAnswer("writingSimilarity")}
              >
                Writings {answerWritingSimilarity?.inProgress ? "(Processing...)" : ""}
              </label>
            )}
            {answerCaselaw && (
              <label className={focusAnswer === "caselaw" ? "active" : ""} onClick={() => setFocusAnswer("caselaw")}>
                Caselaw {answerCaselaw?.inProgress ? "(Processing...)" : ""}
              </label>
            )}
            <label className="ai-request-box__reset-inquiry-btn" onClick={clearInquiry}>
              <ResetIcon />
            </label>
          </div>
          <div className="ai-request-box__focus">
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
            {/* CASELAW */}
            {focusAnswer === "caselaw" && writings ? (
              <>
                {answerCaselaw?.capCases?.map((capCase) => (
                  <CapCasePanel key={capCase.id} capCase={capCase} />
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
`;
