import axios from "axios";
import { useMutation, useQuery } from "react-query";
import { getGideonApiUrl } from "../env";
import { appStore } from "./AppStore";
import { queryClient } from "./queryClient";
import { TUser } from "./useUser";

export type TCase = {
  id: number;
  name?: string;
  organization_id?: number;
  users: TUser[];
};

// GET
const reqCaseGet = async (caseId: number): Promise<TCase> => {
  return axios.get(`${getGideonApiUrl()}/v1/case/${caseId}`).then((res) => res.data.data.case);
};

export const useCase = (caseId: number) => {
  return useQuery<TCase | null>(["case", Number(caseId)], async () => (caseId ? reqCaseGet(caseId) : null), {
    refetchInterval: 1000 * 60,
  });
};

// CREATE
export type TCaseCreate = {
  name?: string;
  organization_id?: number;
  user_id?: number;
};

const reqCasePost = async (data: TCaseCreate): Promise<any> =>
  axios.post(`${getGideonApiUrl()}/v1/case`, data).then((res) => res.data.data.case);

export const useCaseCreate = () =>
  useMutation(async (data: TCaseCreate) => reqCasePost(data), {
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

// USER UPDATE
type TUseCaseUserParams = {
  action: "add" | "remove";
  case_id: number;
  user_id: number;
};

const reqCaseUser = async (params: TUseCaseUserParams): Promise<void> =>
  axios.post(`${getGideonApiUrl()}/v1/case/${params.case_id}/user`, params);

export const useCaseUserUpdate = () =>
  useMutation(async (data: TUseCaseUserParams) => reqCaseUser(data), {
    onSuccess: () => {
      // TODO? other things?
      queryClient.invalidateQueries(["case"]);
      queryClient.invalidateQueries(["cases"]);
    },
  });
