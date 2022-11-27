import { flatten, keyBy, orderBy } from "lodash";
import { Link, useMatch } from "react-router-dom";
import styled from "styled-components";
import { useDocuments } from "../data/useDocuments";

export const TimelineSummary = () => {
  const matches = useMatch("/case/:caseId/*");
  const caseId = Number(matches?.params?.caseId);
  const { data: documents, isSuccess: isSuccessDocuments } = useDocuments(caseId);
  const documentIdMap = keyBy(documents, "id");
  // RENDER
  return (
    <StyledTimelineSummary>
      {!isSuccessDocuments ? (
        <h2>Loading...</h2>
      ) : (
        <table>
          {orderBy(
            flatten((documents ?? []).map((d) => (d.document_events ?? [])?.map((e) => ({ ...e, documentId: d.id })))),
            ["date"],
            ["asc"]
          ).map(({ date, documentId, event }) => (
            <tr key={[documentId, date, event].join("-")}>
              <td className="timeline-summary__td-date">
                <b>{date}</b>
              </td>
              <td className="timeline-summary__td-doc">
                <Link to={`/case/${caseId}/document/${documentId}`}>
                  {documentIdMap[documentId].name?.slice(0, 24)}...
                </Link>
              </td>
              <td className="timeline-summary__td-event">{event}</td>
            </tr>
          ))}
        </table>
      )}
    </StyledTimelineSummary>
  );
};

const StyledTimelineSummary = styled.div`
  font-size: 12px;
  .timeline-summary__td-date {
    font-weight: 900;
    min-width: 72px;
  }
  .timeline-summary__td-doc {
    min-width: 120px;
    max-width: 120px;
    overflow: hidden;
    white-space: nowrap;
    cursor: pointer;
    opacity: 0.5;
    &:hover {
      opacity: 1;
    }
  }
  .timeline-summary__td-event {
    padding: 4px;
  }
`;
