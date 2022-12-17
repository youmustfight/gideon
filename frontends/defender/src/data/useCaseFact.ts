import axios from "axios";
import { useMutation, useQuery } from "react-query";
import { getGideonApiUrl } from "../env";
import { queryClient } from "./queryClient";
import { TCase } from "./useCase";

type TCaseFact = {
  id: number;
  case_id: number;
  text: string;
};

type TUseCaseFactsParams = {
  caseId?: number;
};

// GET
const reqCaseFactsGet = async (params: TUseCaseFactsParams): Promise<TCaseFact[]> => {
  return axios
    .get(`${getGideonApiUrl()}/v1/case_facts`, { params: { case_id: params.caseId } })
    .then((res) => res.data.data.case_facts);
};

export const useCaseFacts = (params: TUseCaseFactsParams) => {
  return useQuery<TCaseFact[]>(["caseFacts", params.caseId], async () => reqCaseFactsGet(params), {
    refetchInterval: 1000 * 15,
  });
};

// CREATE
export type TCaseFactCreateParams = {
  caseId?: number;
  text?: string;
};

const reqCaseFactPost = async ({ caseId, text }: TCaseFactCreateParams): Promise<any> =>
  axios.post(`${getGideonApiUrl()}/v1/case_fact`, {
    case_id: caseId,
    text: text,
  });

export const useCaseFactCreate = (params: TCaseFactCreateParams) =>
  useMutation(async () => reqCaseFactPost(params), {
    onSuccess: () => {
      queryClient.invalidateQueries(["caseFacts"]);
    },
  });

// UPDATE
const reqCaseFactPut = async (caseFact: any): Promise<TCaseFact> =>
  axios.put(`${getGideonApiUrl()}/v1/case_fact/${caseFact.id}`, { case_fact: caseFact });

export const useCaseFactUpdate = () =>
  useMutation(async (data: Partial<TCaseFact>) => reqCaseFactPut({ id: data.id, ...data }), {
    onSuccess: () => {
      queryClient.invalidateQueries(["caseFacts"]);
    },
  });

// DETELE
export const reqCaseFactDelete = async (caseFactId: number | string): Promise<void> =>
  axios.delete(`${getGideonApiUrl()}/v1/case_fact/${caseFactId}`);

export const useCaseFactDelete = () =>
  useMutation(async (caseFactId: number) => reqCaseFactDelete(caseFactId), {
    onSuccess: () => {
      queryClient.invalidateQueries(["caseFacts"]);
    },
  });
