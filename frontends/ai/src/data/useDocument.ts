import axios from "axios";
import { useQuery } from "react-query";
import { getGideonApiUrl } from "../env";
import { TDocument } from "./useDocuments";

// Filters for user via forUser
const reqDocumentGet = async (documentId: number | string): Promise<TDocument[]> =>
  axios.get(`${getGideonApiUrl()}/v1/document/${documentId}`).then((res) => res.data.document);

export const reqDocumentSummarize = async (documentId: number | string): Promise<TDocument[]> =>
  axios.post(`${getGideonApiUrl()}/v1/document/${documentId}/summarize`).then((res) => res.data.document);

export const useDocument = (documentId: number | string) => {
  return useQuery<TDocument[]>(["document", documentId], async () => reqDocumentGet(documentId), {
    refetchInterval: 1000 * 60,
  });
};
