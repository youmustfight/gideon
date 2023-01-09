import axios from "axios";
import { useQuery } from "react-query";
import { getGideonApiUrl } from "../env";
import { TDocument } from "./useDocuments";

// GET
const reqDocumentGet = async (documentId: number): Promise<TDocument> =>
  axios
    .get(`${getGideonApiUrl()}/v1/document/${documentId}`)
    .then((res) => res.data.data.document)
    .catch(() => null);

export const useDocument = (documentId: number) => {
  return useQuery<TDocument>(["document", documentId], async () => reqDocumentGet(documentId), {
    refetchInterval: 1000 * 60,
  });
};

// DELETE
export const reqDocumentDelete = async (documentId: number): Promise<void> =>
  axios.delete(`${getGideonApiUrl()}/v1/document/${documentId}`);

// MISC
export const reqDocumentSummarize = async (documentId: number): Promise<TDocument> =>
  axios.post(`${getGideonApiUrl()}/v1/document/${documentId}/extractions`).then((res) => res.data.data.document);
