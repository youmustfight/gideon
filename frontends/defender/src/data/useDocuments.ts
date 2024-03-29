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
  case_id: number;
  organization_id: number;
  user_id: number;
  name?: string;
  type: "audio" | "docx" | "image" | "pdf" | "video";
  status_processing_files?: "queued" | "completed";
  status_processing_content?: "queued" | "completed";
  status_processing_embeddings?: "queued" | "completed";
  status_processing_extractions?: "queued" | "completed";
  generated_description?: string;
  generated_events?: { date: string; event: string }[];
  generated_summary?: string;
  generated_summary_one_liner?: string;
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
  // mentions_cases_laws: string[];
  // mentions_organizations: string[];
  // mentions_people: string[];
  // pages_as_text: string[];
  // people: Record<string, string>;
};

// Filters for user via forUser
const reqDocumentsGet = async (params: TUseDocumentsParams): Promise<TDocument[]> =>
  axios
    .get(`${getGideonApiUrl()}/v1/documents`, {
      params: { case_id: params.caseId, organization_id: params.organizationId, user_id: params.userId },
    })
    .then((res) => res.data.documents);

type TUseDocumentsParams = {
  caseId?: number;
  organizationId?: number;
  userId?: number;
};

export const useDocuments = ({ caseId, organizationId, userId }: TUseDocumentsParams) => {
  // Setup key for case/org/user context
  const getKey = (): string[] => {
    if (caseId) return ["documents", "case", String(caseId)];
    if (organizationId) return ["documents", "organization", String(organizationId)];
    if (userId) return ["documents", "user", String(userId)];
    return ["documents", "examples"];
  };

  return useQuery<TDocument[]>(getKey(), async () => reqDocumentsGet({ caseId, organizationId, userId }), {
    refetchInterval: 1000 * 15,
  });
};
