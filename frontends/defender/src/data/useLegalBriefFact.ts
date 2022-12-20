import axios from "axios";
import { useMutation, useQuery } from "react-query";
import { getGideonApiUrl } from "../env";
import { queryClient } from "./queryClient";

export type TLegalBriefFact = {
  id: number;
  case_id: number;
  text: string;
};

type TUseLegalBriefFactsParams = {
  caseId?: number;
};

// GET
const reqLegalBriefFactsGet = async (params: TUseLegalBriefFactsParams): Promise<TLegalBriefFact[]> => {
  return axios
    .get(`${getGideonApiUrl()}/v1/legal_brief_facts`, { params: { case_id: params.caseId } })
    .then((res) => res.data.data.legal_brief_facts);
};

export const useLegalBriefFacts = (params: TUseLegalBriefFactsParams) => {
  return useQuery<TLegalBriefFact[]>(["legalBriefFacts", params.caseId], async () => reqLegalBriefFactsGet(params), {
    refetchInterval: 1000 * 15,
  });
};

// CREATE
export type TLegalBriefFactCreateParams = {
  caseId?: number;
  text?: string;
};

const reqLegalBriefFactPost = async ({ caseId, text }: TLegalBriefFactCreateParams): Promise<any> =>
  axios.post(`${getGideonApiUrl()}/v1/legal_brief_fact`, {
    case_id: caseId,
    text: text,
  });

export const useLegalBriefFactCreate = (params: TLegalBriefFactCreateParams) =>
  useMutation(async () => reqLegalBriefFactPost(params), {
    onSuccess: () => {
      queryClient.invalidateQueries(["legalBriefFacts"]);
    },
  });

// UPDATE
const reqLegalBriefFactPut = async (legalBriefFact: any): Promise<TLegalBriefFact> =>
  axios.put(`${getGideonApiUrl()}/v1/legal_brief_fact/${legalBriefFact.id}`, { legal_brief_fact: legalBriefFact });

export const useLegalBriefFactUpdate = () =>
  useMutation(async (data: Partial<TLegalBriefFact>) => reqLegalBriefFactPut({ id: data.id, ...data }), {
    onSuccess: () => {
      queryClient.invalidateQueries(["legalBriefFacts"]);
    },
  });

// DETELE
export const reqLegalBriefFactDelete = async (legalBriefFactId: number | string): Promise<void> =>
  axios.delete(`${getGideonApiUrl()}/v1/legal_brief_fact/${legalBriefFactId}`);

export const useLegalBriefFactDelete = () =>
  useMutation(async (legalBriefFactId: number) => reqLegalBriefFactDelete(legalBriefFactId), {
    onSuccess: () => {
      queryClient.invalidateQueries(["legalBriefFacts"]);
    },
  });
