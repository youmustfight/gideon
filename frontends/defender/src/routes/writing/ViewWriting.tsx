import axios from "axios";
import { saveAs } from "file-saver";
import { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { useDebounce } from "react-use";
import { WritingEditor } from "../../components/WritingEditor/WritingEditor";
import { useWriting, useWritingDelete, useWritingUpdate } from "../../data/useWriting";
import styled from "styled-components";
import { ConfirmButton } from "../../components/ConfirmButton";
import { AppHeader } from "../../components/AppHeader";
import { snakeCase } from "lodash";

type TViewWritingProps = {
  caseId?: number;
};

export const ViewWriting: React.FC<TViewWritingProps> = ({ caseId }) => {
  const navigate = useNavigate();
  const params = useParams();
  const writingId = Number(params.writingId);
  const { data: writing, isSuccess: isSuccessWriting } = useWriting(writingId);
  const { mutateAsync: writingUpdate } = useWritingUpdate();
  const { mutateAsync: writingDelete, isIdle: isIdleDelete } = useWritingDelete();
  // --- save docx helper
  const saveWritingAsDocx = () => {
    axios({ method: "get", url: `/v1/writing/${writingId}/docx`, responseType: "blob" }).then((res) =>
      saveAs(res.data, `${snakeCase(writing!.name)}.docx`)
    );
  };

  // ON MOUNT
  // --- check if writing exists
  useEffect(() => {
    if (!writingId || (isSuccessWriting && !writing)) navigate("/");
  }, [writing, isSuccessWriting]);
  // --- deletion
  const deleteHandler = async () => {
    await writingDelete(writingId);
    navigate(caseId ? `/case/${writing?.case_id}` : "/cases");
  };
  // --- writing props
  const [writingName, setWritingName] = useState(writing?.name);
  const [editorChange, setEditorChange] = useState<{ html: string; text: string }>();
  useDebounce(
    () => {
      writingUpdate({ ...writing, name: writingName, body_html: editorChange?.html, body_text: editorChange?.text });
    },
    1000,
    [editorChange, writingName]
  );

  // RENDER
  return !writing ? null : (
    <>
      <StyledViewWriting>
        {/* HEAD */}
        <div className="writing-header">
          <Link to={caseId ? `/case/${caseId}` : "/cases"}>
            <button>←</button>
          </Link>
          <input
            placeholder="Untitled Name"
            defaultValue={writing?.name}
            value={writingName}
            onChange={(e) => setWritingName(e.target.value)}
          />
          <button>
            <Link to={`/writing/${writingId}/pdf`}>[⬈] PDF</Link>
          </button>
          <button onClick={saveWritingAsDocx}>[⬈] Docx</button>
        </div>

        {/* EDITOR */}
        <WritingEditor html={writing.body_html} onChange={({ html, text }) => setEditorChange({ html, text })} />

        {/* DELETES */}
        <br />
        <br />
        <section>
          <ConfirmButton
            prompts={["Delete Writing", "Yes, Delete Writing"]}
            onClick={deleteHandler}
            disabled={!isIdleDelete}
            style={{ width: "100%" }}
          />
        </section>
      </StyledViewWriting>
    </>
  );
};

export const StyledViewWriting = styled.div`
  margin-top: 10px;
  .writing-title {
    text-align: center;
    padding: 20px 0 6px;
    font-weight: 900;
  }
  .writing-header {
    padding: 20px 24px;
    display: flex;
    background: #fff;
    border-radius: 4px;
    border-bottom: 2px solid #eee;
    & > a {
      max-width: 40px;
    }
    & > input {
      flex-grow: 1;
    }
    & > button {
      width: 80px;
      min-width: 80px;
      max-width: 80px;
      cursor: pointer;
      & > a {
        color: inherit;
        text-decoration: none;
      }
    }
  }
`;
