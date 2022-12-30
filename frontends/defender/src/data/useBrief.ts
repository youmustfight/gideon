import axios from "axios";
import { useMutation, useQuery } from "react-query";
import { getGideonApiUrl } from "../env";
import { queryClient } from "./queryClient";

export type TBriefFact = {
  text: string;
};

export type TBriefIssue = {
  issue: string;
};

export type TBrief = {
  id: number;
  cap_case_id: number;
  case_id: number;
  facts: TBriefFact[];
  issues: TBriefIssue[];
};

type TUseBriefParams = {
  caseId?: number;
  capCaseId?: number;
};

// GET
const reqBriefGet = async (params: TUseBriefParams): Promise<TBrief> => {
  return axios
    .get(
      params.caseId
        ? `${getGideonApiUrl()}/v1/case/${params.caseId}/brief`
        : `${getGideonApiUrl()}/v1/cap/case/${params.capCaseId}/brief`
    )
    .then((res) => res.data?.data?.brief);
};

export const useBrief = (params: TUseBriefParams) => {
  return useQuery<TBrief>(["brief", JSON.stringify(params)], async () => reqBriefGet(params), {
    refetchInterval: 1000 * 15,
  });
};

// CREATE
export type TUseBriefCreateBody = {
  caseId?: number;
  capCaseId?: number;
  issues?: TBriefIssue[];
};

const reqBriefCreate = async (data: TUseBriefCreateBody): Promise<any> =>
  axios
    .post(
      data.caseId
        ? `${getGideonApiUrl()}/v1/case/${data.caseId}/brief`
        : `${getGideonApiUrl()}/v1/cap/case/${data.capCaseId}/brief`,
      { issues: data.issues }
    )
    .then((res) => res.data?.data?.brief);

export const useBriefCreate = () =>
  useMutation(async (data: TUseBriefCreateBody) => reqBriefCreate(data), {
    onSuccess: (data) => {
      // when done, trigger refetch
      queryClient.invalidateQueries(["brief"]);
    },
  });

// UPDATE
const reqBriefPut = async (legalBriefFact: any): Promise<TBrief> =>
  axios.put(`${getGideonApiUrl()}/v1/brief/${legalBriefFact.id}`, { brief: legalBriefFact });

export const useBriefUpdate = () =>
  useMutation(async (data: Partial<TBrief>) => reqBriefPut({ id: data.id, ...data }), {
    onSuccess: () => {
      queryClient.invalidateQueries(["brief"]);
    },
  });
