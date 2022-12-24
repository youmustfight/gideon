import axios from "axios";
import { getGideonApiUrl } from "../env";
import { TDocument, TDocumentContent, TFile } from "./useDocuments";

export type TQueryLocation = {
  score: number;
  document: TDocument;
  document_content: TDocumentContent;
  image_file?: TFile;
  case_id?: number;
  writing_id?: number;
};

export const reqQueryDocument = async ({
  caseId,
  documentId,
  query,
}: {
  caseId: number;
  documentId?: number;
  query: string;
}): Promise<{ answer: string; locations: TQueryLocation[] }> =>
  axios
    .post(`${getGideonApiUrl()}/v1/ai/query-document-answer`, {
      case_id: caseId,
      document_id: documentId,
      question: query,
    })
    .then((res) => ({ answer: res.data.data.answer, locations: res.data.data.locations }));

export const reqQueryDocumentLocations = async ({
  caseId,
  documentId,
  query,
}: {
  caseId: number;
  documentId?: number;
  query: string;
}): Promise<{ locations: TQueryLocation[] }> =>
  axios
    .post(`${getGideonApiUrl()}/v1/ai/query-document-locations`, {
      case_id: caseId,
      document_id: documentId,
      query,
    })
    .then((res) => ({ locations: res.data.data.locations }));

export const reqQueryLegalBriefFactSimilarity = async ({
  caseId,
  organizationId,
  query,
}: {
  caseId?: number;
  organizationId: number;
  query?: string;
}): Promise<{ locations: TQueryLocation[] }> =>
  axios
    .post(`${getGideonApiUrl()}/v1/ai/query-legal-brief-fact-similiarty`, {
      case_id: caseId,
      organization_id: organizationId,
      query,
    })
    .then((res) => ({ locations: res.data.data.locations }));

export const reqQueryWritingSimilarity = async ({
  organizationId,
  query,
}: {
  organizationId?: number;
  query: string;
}): Promise<{ locations: TQueryLocation[] }> =>
  axios
    .post(`${getGideonApiUrl()}/v1/ai/query-writing-similarity`, {
      organization_id: organizationId,
      query: query,
    })
    .then((res) => ({ locations: res.data.data.locations }));
