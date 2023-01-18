import { orderBy } from "lodash";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { ActivityLogIcon, LockClosedIcon, Pencil2Icon, QuestionMarkCircledIcon } from "@radix-ui/react-icons";

import { StyledAIRequestBox } from "../../components/AIRequest/AIRequestBox";
import { useAIRequestStore } from "../../components/AIRequest/AIRequestStore";
import { StyledAIRequestBoxTabs } from "../../components/AIRequest/styled/StyledAIRequestBoxTabs";
import { ConfirmButton } from "../../components/ConfirmButton";
import { DocumentContentLocationBox } from "../../components/DocumentContentLocationBox";
import { WritingEditor } from "../../components/WritingEditor/WritingEditor";
import { useAppStore } from "../../data/AppStore";
import { reqIndexDocument } from "../../data/reqIndexDocument";
import { reqDocumentDelete } from "../../data/useDocument";
import { useDocuments } from "../../data/useDocuments";
import { useUser } from "../../data/useUser";
import { useWritings } from "../../data/useWritings";
import { DocumentViewMultimedia, DocumentViewTranscript } from "../case/ViewCaseDocument";
import { Select } from "../../components/styled/common/Select";
import { Button } from "../../components/styled/common/Button";
import { Input, TextArea } from "../../components/styled/common/Input";
import { P } from "../../components/styled/common/Typography";

const SandboxAIRequest = () => {
  const { data: user } = useUser();
  const {
    aiRequestType,
    answerDetailsLocations,
    answerQuestion,
    answerWriting,
    clearAIRequest,
    inquiry,
    inquiryQuery,
    isAIRequestSubmitted,
    setAIRequestType,
    setAnswerWriting,
    setInquiryScope,
    setInquiryQuery,
    setSummaryScope,
    setWritingInput,
    setWritingScope,
    summarize,
    write,
    writingInput,
  } = useAIRequestStore();
  // --- example documents
  const { data: exampleDocuments = [] } = useDocuments({});
  // --- user documents
  const { data: documents = [], refetch } = useDocuments({ userId: user!.id });
  const [isUploadingDoc, setIsUploadingDoc] = useState(false);
  const [selectedDocumentId, setSelectedDocumentId] = useState("");
  const selectedDocument = [...exampleDocuments, ...documents]?.find((doc) => doc.id === Number(selectedDocumentId));
  // --- document deletion
  const [isDeleting, setIsDeleting] = useState(false);
  const deleteHandler = async () => {
    if (selectedDocument && selectedDocument?.user_id) {
      // checking for user id so we don't delete globals/examples
      setIsDeleting(true);
      await reqDocumentDelete(Number(selectedDocumentId));
      refetch();
      // clear both the query values but also w/e document is selected since that id no longer exists
      clearAIRequest();
      setSelectedDocumentId("");
      setIsDeleting(false);
    }
  };
  // --- writings for selected document + option to view a writing
  const { data: documentWritings = [] } = useWritings({ documentId: selectedDocument?.id });

  // --- do extra calls/setup for changes until we have universal task interface
  const selectSummary = () => {
    setAIRequestType("summarize");
    setSummaryScope("document");
    clearAIRequest();
  };
  const selectAsk = () => {
    setAIRequestType("inquiry");
    setInquiryScope("document");
    clearAIRequest();
  };
  const selectWriteMemo = () => {
    setAIRequestType("write");
    setWritingScope("memoDocument");
    clearAIRequest();
  };
  // @ts-ignore
  const [isFileSubmitted, setIsFileSubmitted] = useState(false);
  // @ts-ignore
  const onSubmitFile = (e) => {
    e.preventDefault();
    setIsFileSubmitted(true);
    // @ts-ignore
    reqIndexDocument(e.target?.file?.files ?? [], { userId: user.id }).then((data) =>
      refetch().then(() => {
        setSelectedDocumentId(data.document.id);
        setIsUploadingDoc(false);
        // --- clear file in input if successful
        e.target.file.value = "";
        setIsFileSubmitted(false);
      })
    );
  };

  // ON MOUNT
  useEffect(() => {
    // --- clear any prior inquiry if we came from an org/case page
    // clearAIRequest();
    // --- initial focus for sandbox should be summarize since it's simpler
    setAIRequestType("summarize");
    setInquiryScope("document");
  }, []);

  // RENDER
  return (
    <StyledSandboxAIRequest>
      <div className="sandbox-ai-request__value-prop">
        <h1>A.I. Sandbox</h1>
        <p>
          Start exploring Gideon AI for <u>documents</u>. <a href="mailto:mark@gideon.foundation">Ask us</a> about AI
          for <u>legal research and writing</u>.
        </p>
      </div>
      <div className="sandbox-ai-request__options">
        <button className={aiRequestType === "summarize" ? "active" : ""} onClick={selectSummary}>
          <div>
            <ActivityLogIcon />
          </div>
          <p>Summarize Document</p>
        </button>
        <button className={aiRequestType === "inquiry" ? "active" : ""} onClick={selectAsk}>
          <div>
            <QuestionMarkCircledIcon />
          </div>
          <p>Document Q&A</p>
        </button>
        <button className={aiRequestType === "write" ? "active" : ""} onClick={selectWriteMemo}>
          <div>
            <Pencil2Icon />
          </div>
          <p>Write Document Memo</p>
        </button>
        {/* <button className="locked">
          <div>
            <LockClosedIcon />
          </div>
          <p>Find Similar Cases</p>
        </button>
        <button className="locked">
          <div>
            <LockClosedIcon />
          </div>
          <p>Write a Motion Draft</p>
        </button> */}
        <button className="locked">
          <div>
            <LockClosedIcon />
          </div>
          <p>Write Case Law Memo</p>
        </button>
      </div>
      <div className="sandbox-ai-request__input">
        {/* DOCUMENT */}
        {["inquiry", "summarize", "write"].includes(aiRequestType) ? (
          <>
            {!isUploadingDoc ? (
              <div className="sandbox-ai-request__input__file-uploader">
                <Select
                  value={selectedDocumentId}
                  disabled={isAIRequestSubmitted}
                  onChange={(e) => setSelectedDocumentId(e.target.value)}
                >
                  <option value="">--- Select a Document ---</option>
                  <optgroup label="Your Uploads">
                    {documents?.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name}
                      </option>
                    ))}
                  </optgroup>
                  <optgroup label="Example Uploads">
                    {/* <option>Gideon vs. Wainwright</option>
                    <option>Inflation Reduction Act</option>
                    <option>U.S. Constitution</option> */}
                    {exampleDocuments?.map((ed) => (
                      <option key={ed.name} value={ed.id}>
                        {ed.name}
                      </option>
                    ))}
                  </optgroup>
                </Select>
                <Button
                  type="submit"
                  disabled={isAIRequestSubmitted}
                  onClick={() => {
                    setIsUploadingDoc(true);
                    setSelectedDocumentId("");
                  }}
                >
                  or Upload
                </Button>
              </div>
            ) : (
              <form className="sandbox-ai-request__input__file-uploader" onSubmit={onSubmitFile}>
                <Button type="button" onClick={() => setIsUploadingDoc(false)}>
                  𝗫
                </Button>
                <Input type="file" name="file" accept=".pdf,.m4a,.mp3,.mp4,.mov,.docx" disabled={isFileSubmitted} />
                <Button type="submit" disabled={isFileSubmitted}>
                  + Upload File
                </Button>
              </form>
            )}
          </>
        ) : null}
        {/* INPUT */}
        {aiRequestType === "inquiry" ? (
          <form
            className="sandbox-ai-request__input__actions"
            onSubmit={(e) => {
              e.preventDefault();
              inquiry({ documentId: Number(selectedDocumentId), userId: user!.id });
            }}
          >
            {/* <p>Ask Gideon AI a question about a document:</p> */}
            <div className="input-row">
              <Input
                placeholder="Ex) What address was the search warrant for?"
                value={inquiryQuery}
                disabled={isAIRequestSubmitted || !selectedDocumentId}
                onChange={(e) => setInquiryQuery(e.target.value)}
              />
              <Button disabled={isAIRequestSubmitted || !selectedDocumentId} type="submit">
                Ask
              </Button>
            </div>
          </form>
        ) : null}
        {aiRequestType === "summarize" ? (
          <form
            className="sandbox-ai-request__input__actions"
            onSubmit={(e) => {
              e.preventDefault();
              summarize({ documentId: Number(selectedDocumentId), userId: user!.id });
            }}
          >
            {/* <p>Get Gideon AI document summary:</p> */}
            {/* <div className="input-row">
              <input
                placeholder="Ex) Family reunification policy"
                value={summaryInput.text}
                disabled={isAIRequestSubmitted}
                onChange={(e) => setSummaryInput({ text: e.target.value })}
              />
              <button disabled={isAIRequestSubmitted} type="submit">
                🔎
              </button>
            </div> */}
          </form>
        ) : null}
        {aiRequestType === "write" ? (
          <form
            className="sandbox-ai-request__input__actions"
            onSubmit={(e) => {
              e.preventDefault();
              write({ documentId: Number(selectedDocumentId), userId: user!.id });
            }}
          >
            {/* <p>Ask Gideon AI questions about a document, and get a written memo:</p> */}
            <div className="input-row">
              {/* "What are examples of oppressive lease clauses? What are examples of favorable clauses on leases for tenants?" */}
              <TextArea
                placeholder="Ex) Question 1... Question 2... Question 3..."
                value={writingInput.promptText}
                disabled={isAIRequestSubmitted || !selectedDocumentId}
                rows={4}
                onChange={(e) => setWritingInput({ promptText: e.target.value })}
                style={{ flexGrow: 1 }}
              ></TextArea>
            </div>
            <div className="input-row">
              <Button
                disabled={isAIRequestSubmitted || !selectedDocumentId || !writingInput.promptText?.length}
                type="submit"
                style={{ flexGrow: 1, maxWidth: "100%", width: "100%" }}
              >
                Write Document Memo
              </Button>
            </div>
          </form>
        ) : null}
      </div>

      {/* ANSWER */}
      {/* --- inquiry */}
      {isAIRequestSubmitted && (answerQuestion || answerDetailsLocations) ? (
        <div className="sandbox-ai-request__answers">
          {answerQuestion && (
            <>
              {answerQuestion?.inProgress && (
                <StyledAIRequestBoxTabs>
                  <label>Answer (Processing...)</label>
                </StyledAIRequestBoxTabs>
              )}
              <div>
                {!answerQuestion?.inProgress && (
                  <P>
                    <b>A:</b> {answerQuestion?.answer}
                  </P>
                )}
              </div>
            </>
          )}
          {answerDetailsLocations && (
            <div>
              {!answerDetailsLocations?.inProgress && (
                <>
                  <P className="source-flavor-text">
                    {answerDetailsLocations?.locations?.length ?? ""}+ Sources Being Used for Answer:
                  </P>
                  <ul>
                    {orderBy(answerDetailsLocations?.locations, ["score"], ["desc"])?.map((l) => (
                      <li key={l.document_content.id}>
                        <DocumentContentLocationBox location={l} />
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          )}
          {/* --- clear */}
          {!answerWriting ? <Button onClick={clearAIRequest}>Clear Answer</Button> : null}
        </div>
      ) : null}
      {/* --- writing */}
      {isAIRequestSubmitted && answerWriting ? (
        <div className="sandbox-ai-request__writing">
          {answerWriting?.inProgress || answerWriting?.writing?.id == null ? (
            <StyledAIRequestBoxTabs>
              <label>Writing (Processing...)</label>
            </StyledAIRequestBoxTabs>
          ) : (
            <div>
              <WritingEditor writingId={answerWriting.writing.id} />
            </div>
          )}
          {answerWriting ? <Button onClick={clearAIRequest}>Clear Writing</Button> : null}
        </div>
      ) : null}
      {/* --- summarize */}
      {aiRequestType === "summarize" && selectedDocument ? (
        <div className="sandbox-ai-request__answers">
          {selectedDocument?.content?.length === 0 ? (
            <StyledAIRequestBoxTabs>
              <label>Summary (Processing...)</label>
            </StyledAIRequestBoxTabs>
          ) : (
            <div>
              <p>{selectedDocument?.generated_summary}</p>
            </div>
          )}
        </div>
      ) : null}

      {/* DOCUMENT -> WRITING */}
      {aiRequestType === "write" && documentWritings?.length > 0 && !answerWriting?.writing ? (
        // <div className="sandbox-ai-request__previous-writings">
        //   <p>
        //     <small>Recent Memos Written</small>
        //   </p>
        //   {documentWritings?.map((dw) => (
        //     <button key={dw.id} onClick={() => setAnswerWriting(dw)}>
        //       {dw.name}
        //     </button>
        //   ))}
        // </div>
        <div className="sandbox-ai-request__previous-writings">
          <p>
            <small>Recent AI Written Memos</small>
          </p>
          <select
            onChange={(e) => {
              const id = Number(e.target.value);
              const writingToRead = documentWritings?.find((dw) => Number(dw.id) === id);
              if (id && writingToRead) setAnswerWriting(writingToRead);
            }}
            style={{ maxWidth: "100%", textAlign: "center" }}
          >
            <option value="">--- Read a Memo ---</option>
            {documentWritings?.slice(0, 6)?.map((dw) => (
              <option key={dw.id} value={dw.id}>
                {dw.name}
              </option>
            ))}
          </select>
        </div>
      ) : null}

      {/* DOCUMENT VIEW */}
      {selectedDocument ? (
        <div className="sandbox-ai-request__transcript">
          <h2>{selectedDocument.name}</h2>
          {selectedDocument.content?.length === 0 ? (
            <P className="processing-content">
              <small>Processing document content...</small>
            </P>
          ) : (
            <>
              <DocumentViewMultimedia document={selectedDocument} />
              <DocumentViewTranscript document={selectedDocument} />
              <hr />
            </>
          )}
          <br />
          <div>
            {/* check if user_id exists, otherwise a person can delete example documents */}
            {selectedDocument?.user_id != null && (
              <ConfirmButton
                prompts={["Delete Document", "Yes, Delete Document"]}
                onClick={deleteHandler}
                disabled={isDeleting}
                style={{ width: "100%" }}
              />
            )}
          </div>
        </div>
      ) : null}
    </StyledSandboxAIRequest>
  );
};

const StyledSandboxAIRequest = styled.div`
  width: 100%;
  .sandbox-ai-request__value-prop {
    padding: 12px;
    margin-bottom: 12px;
    text-align: center;
    h1 {
      font-family: "GT Walsheim";
      font-size: 40px;
      font-weight: 700;
      color: var(--color-black-200);
    }
    p {
      font-family: "GT Walsheim";
      font-weight: 400;
      font-size: 16px;
      margin: 16px 0 12px;
      color: var(--color-black-500);
    }
  }
  .sandbox-ai-request__options {
    width: 540px;
    margin: 0 auto 40px;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    column-gap: 12px;
    row-gap: 24px;
    justify-content: center;
    button {
      height: 100px;
      min-width: 180px;
      display: flex;
      flex-direction: column;
      align-items: center;
      cursor: pointer;
      background: none;
      border: none;
      transition: 400ms;
      &:not(.active) {
        transform: scale3d(0.9, 0.9, 0.9);
      }
      &:hover {
        transform: scale3d(1, 1, 1);
      }
      & > div {
        flex-grow: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--color-blue-500);
        border: 2px solid var(--color-blue-500);
        width: 80px;
        margin: 4px;
        border-radius: 12px;
        svg {
          height: 32px;
          width: 32px;
          path {
            color: white;
          }
        }
      }
      & > p {
        display: flex;
        margin-top: 4px;
        font-weight: 800;
        color: var(--color-blue-500);
      }
      &:not(.active) {
        & > div {
          background: #efefff;
          border: 2px solid #efefff;
          svg {
            path {
              color: var(--color-blue-500);
            }
          }
        }
        & > p {
          color: var(--color-black-500);
        }
      }
      &.locked > div {
        opacity: 0.5;
      }
    }
  }
  .sandbox-ai-request__input {
    margin-top: 24px;
    padding: 24px 20px;
    background: white;
    display: flex;
    flex-direction: column;
    border-radius: 12px;
    box-shadow: var(--effects-box-shadow-500);
    & > form,
    & > div {
      width: 100%;
      // height: 24px;
      display: flex;
      align-items: center;
      input {
        flex-grow: 1;
      }
    }
  }
  .sandbox-ai-request__input__file-uploader {
    display: flex;
    justify-content: space-between;
    width: 100%;
    margin-bottom: 12px;
    select {
      flex-grow: 1;
    }
  }
  .sandbox-ai-request__input__actions {
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    width: 100%;
    p {
      font-size: 16px;
      font-weight: 700;
      margin: 6px 0;
    }
    button,
    input {
      width: 100%;
      margin: 2px 0;
    }
    .input-row {
      display: flex;
      width: 100%;
      input {
        flex-grow: 1;
      }
      button {
        max-width: 80px;
      }
    }
  }
  .sandbox-ai-request__previous-writings {
    width: 540px;
    margin: 12px auto;
    padding: 12px;
    text-align: center;
    p > small {
      font-size: 13px;
      font-style: italic;
      opacity: 0.7;
    }
    select {
      margin-top: 6px;
    }
  }
`;

export const ViewSandbox = () => {
  const navigate = useNavigate();
  const { focusedOrgId } = useAppStore();
  // ON MOUNT
  useEffect(() => {
    // --- if focused on an org navigate to the cases view
    if (focusedOrgId) navigate("/cases");
  }, []);

  // RENDER
  return (
    <StyledViewSandbox>
      <div className="sandbox__centerpiece">
        <SandboxAIRequest />
      </div>
    </StyledViewSandbox>
  );
};

const StyledViewSandbox = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px 24px 24px;
  .sandbox__centerpiece {
    width: 100%;
    margin-bottom: 64px;
    & > p {
      text-align: center;
      margin-bottom: 12px;
    }
    ${StyledAIRequestBox} {
      flex-grow: 1;
    }
  }
  .sandbox-ai-request__answers,
  .sandbox-ai-request__writing {
    padding: 12px 32px;
    background: #f8f8f8;
    & > div > p {
      margin-top: 12px;
      margin-bottom: 24px;
    }
    .source-flavor-text {
      font-size: 14px;
      font-weight: 900;
    }
    & > button {
      width: 100%;
      margin-top: 18px;
      margin-bottom: 6px;
      padding-top: 6px;
    }
  }
  .sandbox-ai-request__answers {
    margin-top: -8px;
    background: var(--color-blue-900);
    border-top: 2px solid var(--color-blue-700);
    box-shadow: var(--effects-box-shadow-500);
  }
  .sandbox-ai-request__writing {
    padding: 12px;
  }
  .sandbox-ai-request__transcript {
    padding: 12px;
    margin-top: 48px;
    background: white;
    & > h2 {
      font-family: "Zodiak";
      text-align: center;
      font-weight: 900;
      font-size: 18px;
      margin: 12px 0;
    }
    .processing-content {
      width: 100%;
      text-align: center;
      font-size: 12px;
      font-style: italic;
    }
  }
`;
