import axios from "axios";
import { intersection } from "lodash";
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import styled from "styled-components";
import { useTeamStore } from "../data/TeamStore";
import { useHighlights } from "../data/useHighlights";
import { HighlightBox } from "./HighlightsBox";

export type TAnswerLocation = {
  filename: string;
  format?: "pdf" | "audio";
  page_number: number;
  minute_number: number;
  score: number;
  text: string;
};

export const AnswerLocationBox = ({ location }: { location: TAnswerLocation }) => {
  return (
    <StyledAnswerLocationBox>
      <b>
        <Link to={`/document/${location.filename}`}>{location.filename}</Link>,{" "}
        {location.format === "pdf" ? (
          <Link to={`/document/${location.filename}#source-text-${location.page_number}`}>
            page {location.page_number}
          </Link>
        ) : (
          <Link to={`/document/${location.filename}#source-text-${location.minute_number}`}>
            minute {location.minute_number}
          </Link>
        )}{" "}
      </b>
      <br />
      <div>"...{location.text}..."</div>
    </StyledAnswerLocationBox>
  );
};

const StyledAnswerLocationBox = styled.div`
  font-size: 12px;
  div {
    margin-top: 4px;
  }
`;

export const QuestionAnswerBox = () => {
  const { data: highlights = [] } = useHighlights();
  const { users } = useTeamStore();
  // --- extras
  const [isShowingExtras, setIsShowingExtras] = useState(false);
  // --- answers state
  const [answer, setAnswer] = useState<{ answer?: string; locations?: TAnswerLocation[] } | null>(null);
  const [isAnswerPending, setIsAnswerPending] = useState(false);
  // --- q1 : Ask Question
  const [answerQuestion, setAnswerQuestion] = useState("");
  const handleQuestion = (e) => {
    e.preventDefault();
    setAnswer(null);
    setIsAnswerPending(true);
    return axios
      .post("http://localhost:3000/queries/question-answer", { question: answerQuestion, index_type: "discovery" })
      .then((res) => {
        setAnswer({ answer: res.data.answer });
        setIsAnswerPending(false);
      });
  };
  // --- q2 : Search for Detail
  const [infoLocationQuestion, setInfoLocationQuestion] = useState("");
  const handleSearchForPage = (e) => {
    e.preventDefault();
    setAnswer(null);
    setIsAnswerPending(true);
    return axios
      .post("http://localhost:3000/queries/query-info-locations", {
        query: infoLocationQuestion,
        index_type: "discovery",
      })
      .then((res) => {
        setAnswer({ locations: res.data.locations });
        setIsAnswerPending(false);
      });
  };
  // --- q3 : Search Highlights
  const [highlightSearchQuery, setHighlightSearchQuery] = useState("");
  const handleHighlightSearch = (e) => {
    e.preventDefault();
    setAnswer(null);
    setIsAnswerPending(true);
    return axios
      .post("http://localhost:3000/queries/highlights-query", {
        query: highlightSearchQuery,
      })
      .then((res) => {
        setAnswer({ highlights: res.data.highlights });
        setIsAnswerPending(false);
      });
  };
  // --- q4 : Summarize Laywer
  const [userToSummarize, setUserToSummarize] = useState("");
  const handleUserSummarizing = () => {
    setAnswer(null);
    setIsAnswerPending(true);
    return axios
      .post("http://localhost:3000/queries/summarize-user", {
        user: userToSummarize,
      })
      .then((res) => {
        setAnswer({ answer: res.data.answer });
        setIsAnswerPending(false);
      });
  };
  // --- q5 : Contrast Laywers
  const [userOneToContrast, setUserOneToContrast] = useState("");
  const [userTwoToContrast, setUserTwoToContrast] = useState("");
  const handleUserContrasting = () => {
    setAnswer(null);
    setIsAnswerPending(true);
    return axios
      .post("http://localhost:3000/queries/contrast-users", {
        user_one: userOneToContrast,
        user_two: userTwoToContrast,
      })
      .then((res) => {
        setAnswer({ answer: res.data.answer });
        setIsAnswerPending(false);
      });
  };

  // RENDER
  return (
    <StyledQuestionAnswerBox>
      <form className="question-box" onSubmit={handleQuestion}>
        <label>
          <span>Ask Question</span>
          <input value={answerQuestion} onChange={(e) => setAnswerQuestion(e.target.value)} />
        </label>
        <button type="submit" disabled={isAnswerPending || !(answerQuestion?.length > 0)}>
          Ask
        </button>
      </form>
      <form className="question-box" onSubmit={handleSearchForPage}>
        <label>
          <span>Search for Detail</span>
          <input
            value={infoLocationQuestion}
            onChange={(e) => setInfoLocationQuestion(e.target.value)}
            disabled={isAnswerPending}
          />
        </label>
        <button type="submit" disabled={isAnswerPending || !(infoLocationQuestion?.length > 0)}>
          Ask
        </button>
      </form>
      {highlights?.length > 0 ? (
        <>
          <form className="question-box" onSubmit={handleHighlightSearch}>
            <label>
              <span>Search Highlights</span>
              <input value={highlightSearchQuery} onChange={(e) => setHighlightSearchQuery(e.target.value)} />
            </label>
            <button type="submit" disabled={isAnswerPending || !(highlightSearchQuery?.length > 0)}>
              Ask
            </button>
          </form>
          {isShowingExtras ? (
            <>
              <div className="question-box">
                <label>
                  <span>Summarize Laywer</span>
                  <select value={userToSummarize} onChange={(e) => setUserToSummarize(e.target.value)}>
                    <option value="">----</option>
                    {intersection(users, Array.from(new Set(highlights.map((hl) => hl.user)))).map((user) => (
                      <option key={user}>{user}</option>
                    ))}
                  </select>
                </label>
                <button
                  type="submit"
                  disabled={isAnswerPending || !(userToSummarize?.length > 0)}
                  onClick={handleUserSummarizing}
                >
                  Summarize
                </button>
              </div>
              <div className="question-box">
                <label>
                  <span>Contrast Laywers</span>
                  <select value={userOneToContrast} onChange={(e) => setUserOneToContrast(e.target.value)}>
                    <option value="">----</option>
                    {intersection(users, Array.from(new Set(highlights.map((hl) => hl.user)))).map((user) => (
                      <option key={user}>{user}</option>
                    ))}
                  </select>
                  <select value={userTwoToContrast} onChange={(e) => setUserTwoToContrast(e.target.value)}>
                    <option value="">----</option>
                    {intersection(users, Array.from(new Set(highlights.map((hl) => hl.user)))).map((user) => (
                      <option key={user}>{user}</option>
                    ))}
                  </select>
                </label>
                <button
                  type="submit"
                  disabled={isAnswerPending || !(userOneToContrast && userTwoToContrast)}
                  onClick={handleUserContrasting}
                >
                  Contrast
                </button>
              </div>
            </>
          ) : (
            <div style={{ fontSize: "8px", marginTop: "6px", textAlign: "center", width: "100%" }}>
              <u onClick={() => setIsShowingExtras(true)}>
                <small>+ Extras</small>
              </u>
            </div>
          )}
        </>
      ) : null}

      {(isAnswerPending || answer != null) && (
        <div className="answer">
          {!!answer ? (
            <>
              {/* TEXT ANSWER */}
              {answer?.answer ? (
                <p>
                  <u>ANSWER:</u> {answer.answer}
                </p>
              ) : null}
              {/* LOCATIONS */}
              {answer?.locations ? (
                <ul>
                  {answer?.locations?.map((l) => (
                    <li>
                      <AnswerLocationBox location={l} />
                    </li>
                  ))}
                </ul>
              ) : null}
              {/* HIGHLIGHTS */}
              {answer?.highlights ? (
                <ul>
                  {answer?.highlights?.map((highlight) => (
                    <HighlightBox highlight={highlight} />
                  ))}
                </ul>
              ) : null}
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
