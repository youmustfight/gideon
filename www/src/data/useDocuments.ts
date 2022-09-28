import axios from "axios";
import { useQuery } from "react-query";

export type TDocument = {
  document_summary: string;
  document_text: string;
  // document_text_vectors: any;
  document_text_by_page: string[];
  document_text_by_minute: string[];
  // document_text_vectors_by_page: any;
  // document_text_vectors_by_paragraph: any;
  // document_text_vectors_by_sentence: any;
  document_type: string;
  event_timeline: string[];
  filename: string;
  index_type: string;
  mentions_cases_laws: string[];
  mentions_organizations: string[];
  mentions_people: string[];
  pages_as_text: string[];
  people: Record<string, string>;
};

// Filters for user via forUser
const reqDocumentsGet = async (): Promise<TDocument[]> =>
  axios.get("http://localhost:3000/documents/indexed").then((res) => res.data.documents);

export const useDocuments = () => {
  return useQuery<TDocument[]>(["documents"], async () => reqDocumentsGet(), {
    refetchInterval: 1000 * 10,
  });
};
