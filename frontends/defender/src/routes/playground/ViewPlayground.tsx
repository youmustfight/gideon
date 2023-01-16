import { orderBy } from "lodash";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
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
import { DocumentViewTranscript } from "../case/ViewCaseDocument";

const PlaygroundAIRequest = () => {
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
    clearAIRequest();
    // --- initial focus for playground should be summarize since it's simpler
    setAIRequestType("inquiry");
    setInquiryScope("document");
  }, []);

  // RENDER
  return (
    <StyledPlaygroundAIRequest>
      <div className="playground-ai-request__options">
        <button className={aiRequestType === "inquiry" ? "active" : ""} onClick={selectAsk}>
          Document Q&A
        </button>
        <button className={aiRequestType === "summarize" ? "active" : ""} onClick={selectSummary}>
          Document Summary
        </button>
        <button className={aiRequestType === "write" ? "active" : ""} onClick={selectWriteMemo}>
          Document Memo
        </button>
      </div>
      <div className="playground-ai-request__input">
        {/* INPUT */}
        {aiRequestType === "inquiry" ? (
          <form
            className="playground-ai-request__input__actions"
            onSubmit={(e) => {
              e.preventDefault();
              inquiry({ documentId: Number(selectedDocumentId), userId: user!.id });
            }}
          >
            <p>Ask Gideon AI a question about a document:</p>
            <div className="input-row">
              <input
                placeholder="Ex) What address was the search warrant for?"
                value={inquiryQuery}
                disabled={isAIRequestSubmitted}
                onChange={(e) => setInquiryQuery(e.target.value)}
              />
              <button disabled={isAIRequestSubmitted || !selectedDocumentId} type="submit">
                🔎
              </button>
            </div>
          </form>
        ) : null}
        {aiRequestType === "summarize" ? (
          <form
            className="playground-ai-request__input__actions"
            onSubmit={(e) => {
              e.preventDefault();
              summarize({ documentId: Number(selectedDocumentId), userId: user!.id });
            }}
          >
            <p>Get Gideon AI document summary:</p>
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
            className="playground-ai-request__input__actions"
            onSubmit={(e) => {
              e.preventDefault();
              write({ documentId: Number(selectedDocumentId), userId: user!.id });
            }}
          >
            <p>Ask Gideon AI questions about a document, and get a written memo:</p>
            <div className="input-row">
              {/* "What are examples of oppressive lease clauses? What are examples of favorable clauses on leases for tenants?" */}
              <textarea
                placeholder="Ex) Question 1... Question 2... Question 3..."
                value={writingInput.promptText}
                disabled={isAIRequestSubmitted}
                rows={4}
                onChange={(e) => setWritingInput({ promptText: e.target.value })}
                style={{ flexGrow: 1 }}
              ></textarea>
            </div>
            <div className="input-row">
              <button
                disabled={isAIRequestSubmitted || !selectedDocumentId || writingInput.promptText?.length < 40}
                type="submit"
                style={{ flexGrow: 1, maxWidth: "100%", width: "100%" }}
              >
                ✏️
              </button>
            </div>
          </form>
        ) : null}
        {/* DOCUMENT */}
        {["inquiry", "summarize", "write"].includes(aiRequestType) ? (
          <>
            {!isUploadingDoc ? (
              <div className="playground-ai-request__input__file-uploader">
                <select
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
                </select>
                <button
                  type="submit"
                  disabled={isAIRequestSubmitted}
                  onClick={() => {
                    setIsUploadingDoc(true);
                    setSelectedDocumentId("");
                  }}
                >
                  + Upload Doc
                </button>
              </div>
            ) : (
              <form className="playground-ai-request__input__file-uploader" onSubmit={onSubmitFile}>
                <button type="button" onClick={() => setIsUploadingDoc(false)}>
                  𝗫
                </button>
                <input type="file" name="file" accept=".pdf,.m4a,.mp3,.mp4,.mov,.docx" disabled={isFileSubmitted} />
                <button type="submit" disabled={isFileSubmitted}>
                  + Upload Doc
                </button>
              </form>
            )}
          </>
        ) : null}
      </div>

      {/* ANSWER */}
      {/* --- inquiry */}
      {isAIRequestSubmitted && (answerQuestion || answerDetailsLocations) ? (
        <div className="playground-ai-request__answers">
          {answerQuestion && (
            <>
              {answerQuestion?.inProgress && (
                <StyledAIRequestBoxTabs>
                  <label>Answer (Processing...)</label>
                </StyledAIRequestBoxTabs>
              )}
              <div>{!answerQuestion?.inProgress && <p>{answerQuestion?.answer}</p>}</div>
            </>
          )}
          {answerDetailsLocations && (
            <div>
              {!answerDetailsLocations?.inProgress && (
                <>
                  <small className="source-flavor-text">
                    {answerDetailsLocations?.locations?.length ?? ""}+ Sources Being Used for Answer:
                  </small>
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
          {!answerWriting ? <button onClick={clearAIRequest}>Clear Answer</button> : null}
        </div>
      ) : null}
      {/* --- writing */}
      {isAIRequestSubmitted && answerWriting ? (
        <div className="playground-ai-request__writing">
          {answerWriting?.inProgress || answerWriting?.writing?.id == null ? (
            <StyledAIRequestBoxTabs>
              <label>Writing (Processing...)</label>
            </StyledAIRequestBoxTabs>
          ) : (
            <div>
              <WritingEditor writingId={answerWriting.writing.id} />
            </div>
          )}
          {answerWriting ? <button onClick={clearAIRequest}>Clear Writing</button> : null}
        </div>
      ) : null}
      {/* --- summarize */}
      {aiRequestType === "summarize" && selectedDocument ? (
        <div className="playground-ai-request__answers">
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
        // <div className="playground-ai-request__previous-writings">
        //   <p>
        //     <small>Recent Memos Written</small>
        //   </p>
        //   {documentWritings?.map((dw) => (
        //     <button key={dw.id} onClick={() => setAnswerWriting(dw)}>
        //       {dw.name}
        //     </button>
        //   ))}
        // </div>
        <div className="playground-ai-request__previous-writings">
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
        <div className="playground-ai-request__transcript">
          <h2>{selectedDocument.name}</h2>
          {selectedDocument.content?.length === 0 ? (
            <p className="processing-content">
              <small>Processing document content...</small>
            </p>
          ) : (
            <>
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
    </StyledPlaygroundAIRequest>
  );
};

const StyledPlaygroundAIRequest = styled.div`
  width: 100%;
  .playground-ai-request__options {
    display: flex;
    margin: 0 auto;
    width: 400px;
    button {
      flex-grow: 1;
      cursor: pointer;
      &:not(.active) {
        opacity: 0.4;
      }
    }
  }
  .playground-ai-request__input {
    margin-top: 24px;
    padding: 12px;
    background: white;
    display: flex;
    flex-direction: column;
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
  .playground-ai-request__input__file-uploader {
    display: flex;
    justify-content: space-between;
    width: 100%;
    margin-bottom: 12px;
    select {
      flex-grow: 1;
    }
  }
  .playground-ai-request__input__actions {
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    width: 100%;
    padding-bottom: 12px;
    border-bottom: 2px solid #fafafa;
    margin-bottom: 12px;
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
  .playground-ai-request__previous-writings {
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

export const ViewPlayground = () => {
  const navigate = useNavigate();
  const { focusedOrgId } = useAppStore();
  // ON MOUNT
  useEffect(() => {
    // --- if focused on an org navigate to the cases view
    if (focusedOrgId) navigate("/cases");
  }, []);

  // RENDER
  return (
    <StyledViewPlayground>
      <div className="playground__centerpiece">
        <PlaygroundAIRequest />
      </div>
    </StyledViewPlayground>
  );
};

const StyledViewPlayground = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120px 24px 24px;
  .playground__centerpiece {
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
  .playground-ai-request__answers,
  .playground-ai-request__writing {
    padding: 12px 32px;
    background: #f8f8f8;
    & > div > p {
      font-size: 14px;
      margin-top: 12px;
      margin-bottom: 24px;
    }
    .source-flavor-text {
      font-size: 11px;
      font-weight: 900;
      padding: 8px;
    }
    & > button {
      width: 100%;
      margin-top: 6px;
      margin-bottom: 6px;
      border: none;
      background: none;
      padding-top: 6px;
      border-top: 2px solid #fafafa;
    }
  }
  .playground-ai-request__writing {
    padding: 12px;
  }
  .playground-ai-request__transcript {
    padding: 12px;
    margin-top: 48px;
    background: white;
    h2 {
      text-align: center;
      font-weight: 900;
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
