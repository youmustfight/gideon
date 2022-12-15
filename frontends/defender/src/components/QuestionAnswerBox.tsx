import axios from "axios";
import { orderBy } from "lodash";
import { useState } from "react";
import { Link } from "react-router-dom";
import styled from "styled-components";
import { useAppStore } from "../data/AppStore";
import { TQueryLocation } from "../data/useDocuments";
import { getGideonApiUrl } from "../env";
import { formatSecondToTime } from "./formatSecondToTime";
import { formatHashForSentenceHighlight } from "./hashUtils";

const StyledAnswerLocationBox = styled.div`
  margin-top: 4px;
  min-height: 20px;
  font-size: 12px;
  display: flex;
  align-items: center;
  background: white;
  padding: 8px;
  border-radius: 6px;
  & > div.answer-location-box__text {
    flex-grow: 1;
    b {
      font-size: 12px;
      display: flex;
      justify-content: space-between;
    }
    p {
      margin: 8px 0 0;
    }
  }
`;

const StyledAnswerLocationBoxImage = styled.div<{ imageSrc: string }>`
  width: 100%;
  max-width: 120px;
  min-height: 60px;
  max-height: 60px;
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  background-image: url(${(props) => props.imageSrc});
  margin-left: 8px;
`;

export const AnswerLocationBox = ({ location }: { location: TQueryLocation }) => {
  const { focusedCaseId } = useAppStore();
  return (
    <StyledAnswerLocationBox>
      <div className="answer-location-box__text">
        <b>
          <Link to={`/case/${focusedCaseId}/document/${location.document.id}`}>{location.document.name ?? "n/a"}</Link>
          <span>
            {location.document.type === "pdf" ? (
              <>
                <Link
                  to={`/case/${focusedCaseId}/document/${location.document.id}#${formatHashForSentenceHighlight(
                    location.document_content.sentence_number ?? location.document_content.sentence_start,
                    location.document_content.sentence_end
                  )}`}
                >
                  {location.document_content.page_number
                    ? `page ${location.document_content.page_number}`
                    : `${formatHashForSentenceHighlight(
                        location.document_content.sentence_number ?? location.document_content.sentence_start,
                        location.document_content.sentence_end
                      )}`}
                </Link>
              </>
            ) : null}
            {["audio", "video"].includes(location.document.type) ? (
              <>
                <Link
                  to={`/case/${focusedCaseId}/document/${location.document.id}#${formatHashForSentenceHighlight(
                    location.document_content.sentence_number ?? location.document_content.sentence_start,
                    location.document_content.sentence_end
                  )}`}
                >
                  {formatSecondToTime(location.document_content.second_start ?? 0)}
                </Link>
              </>
            ) : null}
          </span>
        </b>
        {location.document_content.text && location.document_content.tokenizing_strategy === "sentence" ? (
          <p>"...{location.document_content.text}..."</p>
        ) : null}
      </div>
      {location.image_file ? <StyledAnswerLocationBoxImage imageSrc={location.image_file.upload_url} /> : null}
    </StyledAnswerLocationBox>
  );
};

export const QuestionAnswerBox = () => {
  const { focusedCaseId } = useAppStore();
  // --- answers state
  const [answer, setAnswer] = useState<{ answer?: string; locations?: TQueryLocation[] } | null>(null);
  const [isAnswerPending, setIsAnswerPending] = useState(false);
  // --- answers
  const [answerQuestion, setAnswerQuestion] = useState("");
  const [infoLocationQuestion, setInfoLocationQuestion] = useState("");
  const [highlightSearchQuery, setHighlightSearchQuery] = useState("");
  const [userToSummarize, setUserToSummarize] = useState("");
  const [userOneToContrast, setUserOneToContrast] = useState("");
  const [userTwoToContrast, setUserTwoToContrast] = useState("");
  // --- q1 : Ask Question
  // @ts-ignore
  const handleQuestion = (e) => {
    e.preventDefault();
    setAnswer(null);
    setIsAnswerPending(true);
    return axios
      .post(`${getGideonApiUrl()}/v1/queries/document-query`, {
        case_id: focusedCaseId,
        question: answerQuestion,
        index_type: "discovery",
      })
      .then((res) => {
        setAnswer({ answer: res.data.data.answer, locations: res.data.data.locations });
        setIsAnswerPending(false);
      });
  };
  // --- q2 : Search for Detail
  // @ts-ignore
  const handleSearchForPage = (e) => {
    e.preventDefault();
    setAnswer(null);
    setIsAnswerPending(true);
    return axios
      .post(`${getGideonApiUrl()}/v1/queries/documents-locations`, {
        case_id: focusedCaseId,
        query: infoLocationQuestion,
        index_type: "discovery",
      })
      .then((res) => {
        setAnswer({ locations: res.data.data.locations });
        setIsAnswerPending(false);
      });
  };
  // --- q3 : Search Highlights
  // @ts-ignore
  const handleHighlightSearch = (e) => {
    e.preventDefault();
    setAnswer(null);
    setIsAnswerPending(true);
    return axios
      .post(`${getGideonApiUrl()}/v1/queries/highlights-query`, {
        case_id: focusedCaseId,
        query: highlightSearchQuery,
      })
      .then((res) => {
        // @ts-ignore
        setAnswer({ highlights: res.data.highlights });
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
                        <AnswerLocationBox location={l} />
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
