import axios from "axios";
import { useMutation, useQuery } from "react-query";
import { getGideonApiUrl } from "../env";
import { queryClient } from "./queryClient";
import { TWriting } from "./useWritings";

// GET
const reqWritingGet = async (writingId: number | string): Promise<TWriting> =>
  axios.get(`${getGideonApiUrl()}/v1/writing/${writingId}`).then((res) => res.data.writing);

export const useWriting = (writingId: number | string) => {
  return useQuery<TWriting>(["writing", writingId], async () => reqWritingGet(writingId), {
    refetchInterval: 1000 * 60,
  });
};

// CREATE
export type TWritingCreateParams = {
  bodyHtml?: string;
  bodyText?: string;
  caseId?: number;
  isTemplate: boolean;
  name?: string;
  organizationId?: number;
  forkedWritingId?: number;
};

const reqWritingPost = async (
  { bodyHtml, bodyText, caseId, forkedWritingId, isTemplate, name, organizationId }: TWritingCreateParams,
  runAIWriter: boolean
): Promise<any> =>
  axios
    .post(runAIWriter ? `${getGideonApiUrl()}/v1/writing/ai` : `${getGideonApiUrl()}/v1/writing`, {
      body_html: bodyHtml,
      body_text: bodyText,
      case_id: caseId,
      forked_writing_id: forkedWritingId,
      is_template: isTemplate,
      name,
      organization_id: organizationId,
    })
    .then((res) => res.data.writing);

export const useWritingCreate = () =>
  useMutation(
    async ({ params, runAIWriter }: { params: TWritingCreateParams; runAIWriter: boolean }) =>
      reqWritingPost(params, runAIWriter),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(["writing"]);
        queryClient.invalidateQueries(["writings"]);
      },
    }
  );

// UPDATE
const reqWritingPut = async (writing: any): Promise<TWriting> =>
  axios.put(`${getGideonApiUrl()}/v1/writing/${writing.id}`, { writing: writing }).then((res) => res.data.writing);

export const useWritingUpdate = () =>
  useMutation(async (data: Partial<TWriting>) => reqWritingPut({ id: data.id, ...data }), {
    onSuccess: () => {
      queryClient.invalidateQueries(["writing"]);
      queryClient.invalidateQueries(["writings"]);
    },
  });

// DETELE
export const reqWritingDelete = async (writingId: number | string): Promise<void> =>
  axios.delete(`${getGideonApiUrl()}/v1/writing/${writingId}`);

export const useWritingDelete = () =>
  useMutation(async (writingId: number) => reqWritingDelete(writingId), {
    onSuccess: () => {
      queryClient.invalidateQueries(["writings"]);
    },
  });
