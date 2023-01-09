import { ResetIcon } from "@radix-ui/react-icons";
import { startCase } from "lodash";
import React, { useEffect } from "react";
import { useParams } from "react-router";
import styled from "styled-components";
import { useAppStore } from "../../data/AppStore";
import { useWritings } from "../../data/useWritings";
import { WritingPanel } from "../WritingsBox";
import { AIRequestTypeSelect } from "./AIRequestBox";
import { TWritingScope, useAIRequestStore } from "./AIRequestStore";

export const WriteBox = () => {
  const params = useParams(); // TODO: get from props, not params
  const { focusedOrgId } = useAppStore();
  const {
    answerWriting,
    clearAIRequest,
    isAIRequestSubmitted,
    setWritingInput,
    setWritingScope,
    write,
    writingInput,
    writingScope,
  } = useAIRequestStore();
  const { data: writings } = useWritings({ isTemplate: true, organizationId: focusedOrgId });
  // --- prep some vars for writing
  const selectedWriting = writings?.find((w) => Number(w.id) === Number(writingInput.writingTemplateId));
  const selectedWritingVariables = selectedWriting?.body_text
    .match(/\<\<([a-z|A-Z|\s]*)\>\>/gi)
    ?.map((str) => startCase(str.toLowerCase()));

  // ON MOUNT
  useEffect(() => {
    // --- TODO: if we have a case brief, allow that option
    // if (params.caseId != null) {
    //   setWritingScope("case");
    // } else {
    //   setWritingScope("prompt");
    // }
    setWritingScope("prompt");
  }, []);

  // RENDER
  return (
    <StyledWriteBox>
      <div className="ai-request-box__input rows">
        {/* Doing this inline bc we don't want to take up width on responses */}
        <div className="ai-request-box__input__row">
          <AIRequestTypeSelect disabled={isAIRequestSubmitted} />
          <select
            value={writingInput.writingTemplateId ?? ""}
            disabled={isAIRequestSubmitted}
            onChange={(e) =>
              setWritingInput({
                ...writingInput,
                writingTemplateId: e.target.value,
                writingModel: writings?.find((w) => Number(w.id) === Number(e.target.value)),
              })
            }
            style={{ maxWidth: "100%" }}
          >
            <option value="">--- Select Template ---</option>
            {writings?.map((w) => (
              <option key={w.name} value={w.id}>
                {w.name}
              </option>
            ))}
          </select>
          <select
            value={writingScope}
            disabled={isAIRequestSubmitted}
            onChange={(e) => setWritingScope(e.target.value as TWritingScope)}
            style={{ maxWidth: "100%" }}
          >
            <option value="">--- Select Data Source ---</option>
            <option value="prompt">Using Text Input</option>
            <option value="case" disabled={params.caseId == null}>
              Using Case Brief
            </option>
          </select>
          <button
            type="submit"
            disabled={
              isAIRequestSubmitted ||
              !selectedWriting ||
              (writingScope === "prompt" && writingInput.promptText.length < 20)
            }
            onClick={() => write({ caseId: params?.caseId, organizationId: focusedOrgId })}
          >
            Request
          </button>
        </div>
      </div>
      <div className="prompt-writer">
        {writingScope === "prompt" ? (
          <>
            <div>
              <p>
                Provide the AI details to write, edit, and fill the selected template:{" "}
                <i>"{selectedWriting?.name ?? "___"}"</i>
              </p>
              <p>
                Template variables: <i>{selectedWritingVariables?.join(", ") ?? "___"}</i>
              </p>
            </div>
            <textarea
              disabled={isAIRequestSubmitted}
              placeholder={selectedWritingVariables?.map((str) => `${str}: ...`).join("\n")}
              value={writingInput.promptText}
              rows={5}
              onChange={(e) => setWritingInput({ ...writingInput, promptText: e.target.value })}
            />
          </>
        ) : null}
      </div>

      {isAIRequestSubmitted && (
        <>
          {/* TABS */}
          <div className="ai-request-box__tabs">
            <label className="active">Writing {answerWriting?.inProgress ? "(Processing...)" : ""}</label>
            <label className="ai-request-box__reset-inquiry-btn" onClick={clearAIRequest}>
              <ResetIcon />
            </label>
          </div>
          {/* FOCUS */}
          <div className="ai-request-box__focus">
            {answerWriting?.writing ? <WritingPanel writing={answerWriting?.writing} /> : null}
          </div>
        </>
      )}
    </StyledWriteBox>
  );
};

const StyledWriteBox = styled.div`
  .ai-request-box__input__row > select {
    flex-grow: 1;
  }
  .prompt-writer {
    display: flex;
    flex-direction: column;
    p {
      margin: 5px 0;
      font-size: 14px;
    }
    i {
      font-style: italic;
    }
  }
`;
