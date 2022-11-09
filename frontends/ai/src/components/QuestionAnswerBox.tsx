import axios from "axios";
import { intersection } from "lodash";
import React, { useEffect, useState } from "react";
import { Link, useMatch } from "react-router-dom";
import styled from "styled-components";
import { useTeamStore } from "../data/TeamStore";
import { useCase } from "../data/useCase";
import { useCases } from "../data/useCases";
import { TDocument, TDocumentContent, TQueryLocation } from "../data/useDocuments";
import { useHighlights } from "../data/useHighlights";
import { HighlightBox } from "./HighlightsBox";

export const AnswerLocationBox = ({ location }: { location: TQueryLocation }) => {
  // TODO: replace with useCase() hook
  const matches = useMatch("/case/:caseId/*")?.params;
  const caseId = Number(matches?.caseId);
  return (
    <StyledAnswerLocationBox>
      <b>
        <Link to={`/case/${caseId}/document/${location.document.id}`}>{location.document.name ?? "n/a"}</Link>
        {location.document.type === "pdf" ? (
          <>
            ,{" "}
            <Link
              to={`/case/${caseId}/document/${location.document.id}#source-text-${location.document_content.page_number}`}
            >
              page {location.document_content.page_number}
            </Link>
          </>
        ) : null}
        {location.document.type === "audio" ? (
          <>
            ,{" "}
            <Link
              to={`/case/${caseId}/document/${location.document.id}#source-text-${location.document_content.minute_number}`}
            >
              minute {location.document_content.minute_number}
            </Link>
          </>
        ) : null}
      </b>
      <br />
      <div>"...{location.document_content.text}..."</div>
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
  // --- answers state
  const [answer, setAnswer] = useState<{ answer?: string; locations?: TQueryLocation[] } | null>(null);
  const [isAnswerPending, setIsAnswerPending] = useState(false);
  // --- q1 : Ask Question
  const [answerQuestion, setAnswerQuestion] = useState("");
  const handleQuestion = (e) => {
    e.preventDefault();
    setAnswer(null);
    setIsAnswerPending(true);
    return axios
      .post("http://localhost:3000/v1/queries/document-query", { question: answerQuestion, index_type: "discovery" })
      .then((res) => {
        setAnswer({ answer: res.data.answer, locations: res.data.locations });
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
      .post("http://localhost:3000/v1/queries/documents-locations", {
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
      .post("http://localhost:3000/v1/queries/highlights-query", {
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
      .post("http://localhost:3000/v1/queries/summarize-user", {
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
      .post("http://localhost:3000/v1/queries/contrast-users", {
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
      <form className="question-box" onSubmit={handleHighlightSearch}>
        <label>
          <span>Search Highlights</span>
          <input disabled value={highlightSearchQuery} onChange={(e) => setHighlightSearchQuery(e.target.value)} />
        </label>
        <button type="submit" disabled={isAnswerPending || !(highlightSearchQuery?.length > 0)}>
          Ask
        </button>
      </form>
      <div className="question-box">
        <label>
          <span>Summarize Laywer</span>
          <select disabled value={userToSummarize} onChange={(e) => setUserToSummarize(e.target.value)}>
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
        <button
          type="submit"
          disabled={isAnswerPending || !(userOneToContrast && userTwoToContrast)}
          onClick={handleUserContrasting}
        >
          Contrast
        </button>
      </div>

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
