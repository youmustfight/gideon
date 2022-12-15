import axios from "axios";
import { useMutation, useQuery } from "react-query";
import { getGideonApiUrl } from "../env";
import { appStore } from "./AppStore";
import { queryClient } from "./queryClient";

export type TCase = {
  id: number;
  name?: string;
};

// GET
const reqCaseGet = async (caseId: number): Promise<TCase> => {
  return axios.get(`${getGideonApiUrl()}/v1/case/${caseId}`).then((res) => res.data.case);
};

export const useCase = (caseId: number) => {
  return useQuery<TCase | null>(["case", Number(caseId)], async () => (caseId ? reqCaseGet(caseId) : null), {
    refetchInterval: 1000 * 60,
  });
};

// CREATE
const reqCasePost = async ({ userId }: any): Promise<any> =>
  axios.post(`${getGideonApiUrl()}/v1/case`, { userId }).then((res) => res.data.case);

export const useCaseCreate = () =>
  useMutation(async ({ userId }: { userId: number }) => reqCasePost({ userId }), {
    onSuccess: (data) => {
      // Refetch data
      queryClient.invalidateQueries(["case"]);
      queryClient.invalidateQueries(["cases"]);
      // Set new focus
      appStore.getState().setFocusedCaseId(data.id);
    },
  });

// UPDATE
const reqCasePut = async (cse: any): Promise<TCase> =>
  axios.put(`${getGideonApiUrl()}/v1/case/${cse.id}`, { case: cse }).then((res) => res.data.case);

export const useCaseUpdate = () =>
  useMutation(async (data: Partial<TCase>) => reqCasePut({ id: data.id, ...data }), {
    onSuccess: () => {
      queryClient.invalidateQueries(["case"]);
      queryClient.invalidateQueries(["cases"]);
    },
  });

// MISC
export const reqCaseAILocksReset = async (caseId: number): Promise<TCase> => {
  return axios.put(`${getGideonApiUrl()}/v1/case/${caseId}/ai_action_locks_reset`).then((res) => res.data);
};

export const reqCaseReindexAllDocuments = async (caseId: number): Promise<TCase> => {
  return axios.put(`${getGideonApiUrl()}/v1/case/${caseId}/reindex_all_documents`).then((res) => res.data);
};
