import axios from "axios";
import { orderBy } from "lodash";
import { useState } from "react";
import styled from "styled-components";
import { useAppStore } from "../data/AppStore";
import { TQueryLocation } from "../data/useDocuments";
import { reqQueryDocument, reqQueryDocumentLocations } from "../data/useQueryAI";
import { getGideonApiUrl } from "../env";
import { LocationBox } from "./LocationBox";

export const QuestionAnswerBox = () => {
  const { focusedCaseId } = useAppStore();
  // --- answers state
  const [answer, setAnswer] = useState<{ answer?: string; locations?: TQueryLocation[] } | null>(null);
  const [isAnswerPending, setIsAnswerPending] = useState(false);
  // --- answers
  const [answerQuestion, setAnswerQuestion] = useState("");
  const [infoLocationQuestion, setInfoLocationQuestion] = useState("");
  // --- q1 : Ask Question
  // @ts-ignore
  const handleQuestion = (e) => {
    e.preventDefault();
    setAnswer(null);
    setIsAnswerPending(true);
    return reqQueryDocument({
      caseId: focusedCaseId,
      query: answerQuestion,
    }).then(({ answer, locations }) => {
      setAnswer({ answer, locations });
      setIsAnswerPending(false);
    });
  };
  // --- q2 : Search for Detail
  // @ts-ignore
  const handleSearchForPage = (e) => {
    e.preventDefault();
    setAnswer(null);
    setIsAnswerPending(true);
    return reqQueryDocumentLocations({ caseId: focusedCaseId, query: infoLocationQuestion }).then(({ locations }) => {
      setAnswer({ locations });
      setIsAnswerPending(false);
    });
  };

  // RENDER
  return (
    <StyledQuestionAnswerBox>
      <form className="question-box" onSubmit={handleQuestion}>
        <label>
          {/* <span>Ask Question</span> */}
          <input
            placeholder="Where did the search warrant authorize a raid on?"
            value={answerQuestion}
            onChange={(e) => setAnswerQuestion(e.target.value)}
          />
        </label>
        <button type="submit" disabled={isAnswerPending || !(answerQuestion?.length > 0)}>
          Ask Question
        </button>
      </form>
      <form className="question-box" onSubmit={handleSearchForPage}>
        <label>
          {/* <span>Search for Detail</span> */}
          <input
            placeholder="Presidential authority on disclosure"
            value={infoLocationQuestion}
            onChange={(e) => setInfoLocationQuestion(e.target.value)}
            disabled={isAnswerPending}
          />
        </label>
        <button type="submit" disabled={isAnswerPending || !(infoLocationQuestion?.length > 0)}>
          Find Detail
        </button>
      </form>
      {/* <form className="question-box" onSubmit={handleHighlightSearch}>
        <label>
          <span>Search Highlights</span>
          <input disabled value={highlightSearchQuery} onChange={(e) => setHighlightSearchQuery(e.target.value)} />
        </label>
        <button type="submit" disabled={isAnswerPending || !(highlightSearchQuery?.length > 0)}>
          Ask
        </button>
      </form> */}
      {/* <div className="question-box">
        <label>
          <span>Summarize Laywer</span>
          <select disabled value={userToSummarize} onChange={(e) => setUserToSummarize(e.target.value)}>
            <option value="">----</option>
            {intersection(users, Array.from(new Set(highlights.map((hl) => hl.user)))).map((user) => (
              <option key={user}>{user}</option>
            ))}
          </select>
        </label>
        <button type="submit" disabled={isAnswerPending || !(userToSummarize?.length > 0)}>
          Summarize
        </button>
      </div> */}
      {/* <div className="question-box">
        <label>
          <span>Contrast Laywers</span>
          <select disabled value={userOneToContrast} onChange={(e) => setUserOneToContrast(e.target.value)}>
            <option value="">----</option>
            {intersection(users, Array.from(new Set(highlights.map((hl) => hl.user)))).map((user) => (
              <option key={user}>{user}</option>
            ))}
          </select>
          <select disabled value={userTwoToContrast} onChange={(e) => setUserTwoToContrast(e.target.value)}>
            <option value="">----</option>
            {intersection(users, Array.from(new Set(highlights.map((hl) => hl.user)))).map((user) => (
              <option key={user}>{user}</option>
            ))}
          </select>
        </label>
        <button type="submit" disabled={isAnswerPending || !(userOneToContrast && userTwoToContrast)}>
          Contrast
        </button>
      </div> */}

      {(isAnswerPending || answer != null) && (
        <div className="answer">
          {!!answer ? (
            <>
              {/* TEXT ANSWER */}
              {answer?.answer ? (
                <p>
                  <u>ANSWER:</u>
                  <br />
                  <br />
                  {answer.answer}
                </p>
              ) : null}
              {/* LOCATIONS */}
              {answer?.locations ? (
                <>
                  <br />
                  <p>
                    <u>SOURCES:</u>
                  </p>
                  <ul>
                    {orderBy(answer?.locations, ["score"], ["desc"])?.map((l) => (
                      <li key={l.document_content.id}>
                        <LocationBox location={l} />
                      </li>
                    ))}
                  </ul>
                </>
              ) : null}
              {/* HIGHLIGHTS */}
              {/* {answer?.highlights ? (
                <ul>
                  {answer?.highlights?.map((highlight) => (
                    <HighlightBox highlight={highlight} />
                  ))}
                </ul>
              ) : null} */}
              {/* CLEAR RESULTS */}
              <button className="reset-answer" onClick={() => setAnswer(null)}>
                Clear Results
              </button>
            </>
          ) : null}
        </div>
      )}
    </StyledQuestionAnswerBox>
  );
};

const StyledQuestionAnswerBox = styled.div`
  display: flex;
  flex-direction: column;
  .question-box {
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
  }
  .answer {
    border-top: 2px solid #eee;
    margin-top: 8px;
    padding-top: 8px;
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
  .reset-answer {
    width: 100%;
    font-size: 11px;
    margin-top: 6px;
  }
`;
