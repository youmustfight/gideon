import { orderBy } from "lodash";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import styled from "styled-components";
import { StyledAIRequestBox } from "../../components/AIRequest/AIRequestBox";
import { useAIRequestStore } from "../../components/AIRequest/AIRequestStore";
import { StyledAIRequestBoxTabs } from "../../components/AIRequest/styled/StyledAIRequestBoxTabs";
import { ConfirmButton } from "../../components/ConfirmButton";
import { DocumentContentLocationBox } from "../../components/DocumentContentLocationBox";
import { useAppStore } from "../../data/AppStore";
import { reqIndexDocument } from "../../data/reqIndexDocument";
import { reqDocumentDelete } from "../../data/useDocument";
import { useDocuments } from "../../data/useDocuments";
import { useUser } from "../../data/useUser";
import { DocumentViewTranscript } from "../case/ViewCaseDocument";

const PlaygroundAIRequest = () => {
  const { data: user } = useUser();
  const {
    aiRequestType,
    answerDetailsLocations,
    answerQuestion,
    clearAIRequest,
    inquiry,
    inquiryQuery,
    isAIRequestSubmitted,
    setAIRequestType,
    setInquiryScope,
    setInquiryQuery,
    setSummaryScope,
    summarize,
  } = useAIRequestStore();
  const { data: documents, refetch } = useDocuments({ userId: user!.id });
  const [isUploadingDoc, setIsUploadingDoc] = useState(false);
  const [selectedDocumentId, setSelectedDocumentId] = useState("");
  const selectedDocument = documents?.find((doc) => doc.id === Number(selectedDocumentId));
  // --- document deletion
  const [isDeleting, setIsDeleting] = useState(false);
  const deleteHandler = async () => {
    if (selectedDocument && selectedDocument?.user_id) {
      // checking for user id so we don't delete globals/examples
      setIsDeleting(true);
      await reqDocumentDelete(Number(selectedDocumentId));
      refetch();
      clearAIRequest();
      setIsDeleting(false);
    }
  };

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
  // @ts-ignore
  const onSubmitFile = (e) => {
    e.preventDefault();
    // @ts-ignore
    reqIndexDocument(e.target?.file?.files ?? [], { userId: user.id }).then((data) =>
      refetch().then(() => {
        setSelectedDocumentId(data.document.id);
        setIsUploadingDoc(false);
      })
    );
    // --- clear file in input if successful
    e.target.file.value = "";
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
      </div>
      <div className="playground-ai-request__input">
        {/* INPUT */}
        {aiRequestType === "inquiry" ? (
          <form
            className="playground-ai-request__input__actions"
            onSubmit={(e) => {
              e.preventDefault();
              inquiry({ documentId: selectedDocumentId, userId: user!.id });
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
              summarize({ documentId: selectedDocumentId, userId: user!.id });
            }}
          >
            <p>Get document summary from Gideon AI:</p>
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
        {/* DOCUMENT */}
        {["inquiry", "summarize"].includes(aiRequestType) ? (
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
                    <option>Gideon vs. Wainwright</option>
                    <option>Inflation Reduction Act</option>
                    <option>U.S. Constitution</option>
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
                <input type="file" name="file" accept=".pdf,.m4a,.mp3,.mp4,.mov,.docx" />
                <button type="submit">+ Upload Doc</button>
              </form>
            )}
          </>
        ) : null}
      </div>

      {/* ANSWER */}
      {isAIRequestSubmitted ? (
        <div className="playground-ai-request__answers">
          {/* --- inquiry */}
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
          <button onClick={clearAIRequest}>Clear Answer</button>
        </div>
      ) : null}
      {/* --- summarize */}
      {aiRequestType === "summarize" ? (
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
              <section>
                <ConfirmButton
                  prompts={["Delete Document", "Yes, Delete Document"]}
                  onClick={deleteHandler}
                  disabled={isDeleting}
                  style={{ width: "100%" }}
                />
              </section>
            </>
          )}
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
  .playground-ai-request__answers {
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
