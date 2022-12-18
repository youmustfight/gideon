import axios from "axios";
import { getGideonApiUrl } from "../env";
import { TQueryLocation } from "./useDocuments";

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
