import axios from "axios";
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import styled from "styled-components";

type TAnswerLocation = {
  filename: string;
  format?: "pdf" | "audio";
  page_number: number;
  minute_number: number;
  score: number;
  text: string;
};

export const QuestionAnswerBox = () => {
  // SETUP
  const [answerQuestion, setAnswerQuestion] = useState("");
  const [infoLocationQuestion, setInfoLocationQuestion] = useState("");
  const [answer, setAnswer] = useState<{ answer?: string; locations?: TAnswerLocation[] } | null>(null);
  const [isAnswerPending, setIsAnswerPending] = useState(false);
  // --- helpers
  const handleQuestion = (e) => {
    e.preventDefault();
    setAnswer(null);
    setIsAnswerPending(true);
    return axios
      .post("http://localhost:3000/question-answer", { question: answerQuestion, index_type: "discovery" })
      .then((res) => {
        setAnswer({ answer: res.data.answer });
        setIsAnswerPending(false);
      });
  };
  const handleSearchForPage = (e) => {
    e.preventDefault();
    setAnswer(null);
    setIsAnswerPending(true);
    return axios
      .post("http://localhost:3000/question-info-location", { question: infoLocationQuestion, index_type: "discovery" })
      .then((res) => {
        setAnswer({ locations: res.data.locations });
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
          <span>Get Detail Location</span>
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
      {(isAnswerPending || answer != null) && (
        <div className="answer">
          {!!answer ? (
            <>
              {answer?.answer ? (
                <p>
                  <u>ANSWER:</u> {answer.answer}
                </p>
              ) : null}
              {answer?.locations ? (
                <>
                  <p>
                    <u>FOUND IN:</u>
                  </p>
                  <ul>
                    {answer?.locations?.map((l) => (
                      <li>
                        <b>
                          <Link to={`/document/${l.filename}`}>{l.filename}</Link>,{" "}
                          {l.format === "pdf" ? (
                            <Link to={`/document/${l.filename}#source-text-${l.page_number}`}>
                              page {l.page_number}
                            </Link>
                          ) : (
                            <Link to={`/document/${l.filename}#source-text-${l.minute_number}`}>
                              minute {l.minute_number}
                            </Link>
                          )}{" "}
                        </b>
                        <br />
                        <span>"...{l.text}..."</span>
                      </li>
                    ))}
                  </ul>
                </>
              ) : null}
            </>
          ) : null}
          {isAnswerPending ? <p className="searching"></p> : null}
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
    input {
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
`;
