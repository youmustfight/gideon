import axios from "axios";
import { useQuery } from "react-query";
import { getGideonApiUrl } from "../env";

export type TCase = {
  id: number;
  name?: string;
};

const reqCaseGet = async (caseId: number | string): Promise<TCase> => {
  return axios.get(`${getGideonApiUrl()}/v1/case/${caseId}`).then((res) => res.data.case);
};

export const reqCaseAILocksReset = async (caseId: number | string): Promise<TCase> => {
  return axios.put(`${getGideonApiUrl()}/v1/case/${caseId}/ai_action_locks_reset`).then((res) => res.data);
};

export const reqCaseReindexAllDocuments = async (caseId: number | string): Promise<TCase> => {
  return axios.put(`${getGideonApiUrl()}/v1/case/${caseId}/reindex_all_documents`).then((res) => res.data);
};

export const useCase = (caseId: number | string | undefined) => {
  return useQuery<TCase | null>(["case", Number(caseId)], async () => (caseId ? reqCaseGet(caseId) : null), {
    refetchInterval: 1000 * 60,
  });
};
