import axios from "axios";
import { useQuery } from "react-query";
import { getGideonApiUrl } from "../env";

export type TDocumentSentenceTextVector = { page_number: number; text: string; vector: number[] };

export type TDocumentContent = {
  id: number;
  document_id: number;
  // text
  text: string;
  tokenizing_strategy: string;
  page_number: string;
  sentence_number?: number;
  sentence_start?: number;
  sentence_end?: number;
  // image
  image_patch_size?: number;
  // audio/video
  second_start?: number;
  second_end?: number;
};

export type TFile = {
  id: number;
  document_id: number;
  filename: string;
  mime_type: string;
  upload_key: string;
  upload_url: string;
  upload_thumbnail_url: string;
};

export type TDocument = {
  // v2 (now with a database/orm)
  id: number;
  name?: string;
  type: "audio" | "image" | "pdf" | "video";
  status_processing_files?: "queued" | "completed";
  status_processing_content?: "queued" | "completed";
  status_processing_embeddings?: "queued" | "completed";
  status_processing_extractions?: "queued" | "completed";
  document_description?: string;
  document_events?: { date: string; event: string }[];
  document_summary?: string;
  content?: TDocumentContent[];
  files?: TFile[];
  // v1 (when saving everything to disk as json)
  // document_summary: string;
  // document_text: string;
  // // document_text_vectors: any;
  // document_text_by_page: string[];
  // document_text_by_minute: string[];
  // // document_text_vectors_by_page: any;
  // // document_text_vectors_by_paragraph: any;
  // document_text_vectors_by_sentence: TDocumentSentenceTextVector[];
  // document_type: string;
  // event_timeline: string[];
  // filename: string;
  // format: "audio" | "pdf";
  // index_type: string;
  // mentions_cases_laws: string[];
  // mentions_organizations: string[];
  // mentions_people: string[];
  // pages_as_text: string[];
  // people: Record<string, string>;
};

export type TQueryLocation = {
  score: number;
  document: TDocument;
  document_content: TDocumentContent;
  image_file?: TFile;
};

// Filters for user via forUser
const reqDocumentsGet = async (caseId: number): Promise<TDocument[]> =>
  axios.get(`${getGideonApiUrl()}/v1/documents`, { params: { case_id: caseId } }).then((res) => res.data.documents);

export const useDocuments = (caseId: number) => {
  return useQuery<TDocument[]>(["documents"], async () => reqDocumentsGet(caseId), {
    refetchInterval: 1000 * 15,
  });
};
