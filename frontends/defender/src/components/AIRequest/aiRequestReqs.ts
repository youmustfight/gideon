import axios from "axios";
import { getGideonApiUrl } from "../../env";
import { TCapCase } from "../../data/useCapCase";
import { TDocument, TDocumentContent, TFile } from "../../data/useDocuments";

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
  userId,
}: {
  caseId: number;
  documentId?: number;
  query: string;
  userId?: number;
}): Promise<{ answer: string; locations: TQueryLocation[] }> =>
  axios
    .post(`${getGideonApiUrl()}/v1/ai/query-document-answer`, {
      case_id: caseId,
      document_id: documentId,
      query,
      user_id: userId,
    })
    .then((res) => ({ answer: res.data.data.answer, locations: res.data.data.locations }));

export const reqQueryDocumentLocations = async ({
  caseId,
  documentId,
  query,
  userId,
}: {
  caseId: number;
  documentId?: number;
  query: string;
  userId?: number;
}): Promise<{ locations: TQueryLocation[] }> =>
  axios
    .post(`${getGideonApiUrl()}/v1/ai/query-document-locations`, {
      case_id: caseId,
      document_id: documentId,
      query,
      user_id: userId,
    })
    .then((res) => ({ locations: res.data.data.locations }));

export const reqQueryBriefFactSimilarity = async ({
  caseId,
  organizationId,
  query,
}: {
  caseId?: number;
  organizationId: number;
  query?: string;
}): Promise<{ locations: TQueryLocation[] }> =>
  axios
    .post(`${getGideonApiUrl()}/v1/ai/query-brief-fact-similiarty`, {
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

export const reqQueryCaselaw = async ({
  query,
}: {
  organizationId?: number;
  query: string;
}): Promise<{ capCases: TCapCase[] }> =>
  axios
    .get(`${getGideonApiUrl()}/v1/cap/case/search`, {
      params: { query },
    })
    .then((res) => ({ capCases: res.data.data.cap_cases }));

export const reqQuerySummarize = async ({
  // caseId
  text,
}: {
  text: string;
}): Promise<{ summary: string }> =>
  axios
    .post(`${getGideonApiUrl()}/v1/ai/summarize`, {
      text,
    })
    .then((res) => ({ summary: res.data.data.summary }));
