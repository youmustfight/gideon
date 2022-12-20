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
  query,
}: {
  caseId: number;
  query: string;
}): Promise<{ answer: string; locations: TQueryLocation[] }> =>
  axios
    .post(`${getGideonApiUrl()}/v1/ai/query-document-answer`, {
      case_id: caseId,
      question: query,
    })
    .then((res) => ({ answer: res.data.data.answer, locations: res.data.data.locations }));

export const reqQueryDocumentLocations = async ({
  caseId,
  query,
}: {
  caseId: number;
  query: string;
}): Promise<{ locations: TQueryLocation[] }> =>
  axios
    .post(`${getGideonApiUrl()}/v1/ai/query-document-locations`, {
      case_id: caseId,
      query,
    })
    .then((res) => ({ locations: res.data.data.locations }));

export const reqQueryLegalBriefFactSimilarity = async ({
  caseId,
}: {
  caseId: number;
}): Promise<{ locations: TQueryLocation[] }> =>
  axios
    .post(`${getGideonApiUrl()}/v1/ai/query-legal-brief-fact-similiarty`, {
      case_id: caseId,
    })
    .then((res) => ({ locations: res.data.data.locations }));

export const reqQueryWritingSimilarity = async ({
  caseId,
  query,
}: {
  caseId?: number;
  query: string;
}): Promise<{ locations: TQueryLocation[] }> =>
  axios
    .post(`${getGideonApiUrl()}/v1/ai/query-writing-similarity`, {
      case_id: caseId,
      query: query,
    })
    .then((res) => ({ locations: res.data.data.locations }));
