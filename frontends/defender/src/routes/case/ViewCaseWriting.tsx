import { useState } from "react";
import { Link, useMatch, useNavigate } from "react-router-dom";
import { useDebounce } from "react-use";
import { WritingEditor } from "../../components/WritingEditor/WritingEditor";
import { useWriting } from "../../data/useWriting";
import { reqWritingDelete } from "../../data/useWritingDelete";
import { useWritingUpdate } from "../../data/useWritingUpdate";
import styled from "styled-components";

export const ViewCaseWriting = () => {
  const navigate = useNavigate();
  const { caseId, writingId } = useMatch("/case/:caseId/writing/:writingId")?.params;
  const { data: writing } = useWriting(writingId);
  const { mutateAsync: writingUpdate } = useWritingUpdate();
  // --- deletion
  const [isDeleting, setIsDeleting] = useState(false);
  const deleteHandler = async () => {
    setIsDeleting(true);
    await reqWritingDelete(writingId);
    navigate(`/case/${writing?.case_id}`);
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
    <StyledViewCaseWriting>
      {/* HEAD */}
      <div className="writing-header">
        <Link to={`/case/${caseId}`}>
          <button>←</button>
        </Link>
        <input
          placeholder="Untitled Name"
          defaultValue={writing?.name}
          value={writingName}
          onChange={(e) => setWritingName(e.target.value)}
        />
        <button>
          <a href={`/writing/${writingId}/pdf`} target="_blank">
            Preview PDF
          </a>
        </button>
      </div>

      {/* EDITOR */}
      <WritingEditor html={writing.body_html} onChange={({ html, text }) => setEditorChange({ html, text })} />

      {/* DELETES */}
      <br />
      <br />
      <section>
        <button disabled={isDeleting} onClick={deleteHandler} style={{ width: "100%" }}>
          Delete Writing
        </button>
      </section>
    </StyledViewCaseWriting>
  );
};

export const StyledViewCaseWriting = styled.div`
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
      width: 150px;
      min-width: 150px;
      max-width: 150px;
    }
  }
`;
