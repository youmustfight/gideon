import axios from "axios";
import { useMutation } from "react-query";
import { getGideonApiUrl } from "../env";
import { queryClient } from "./queryClient";

const reqWritingPost = async ({ caseId }: any): Promise<any> =>
  axios.post(`${getGideonApiUrl()}/v1/writing`, { case_id: caseId }).then((res) => res.data.writing);

export const useWritingCreate = () =>
  useMutation(async ({ caseId }: { caseId: number }) => reqWritingPost({ caseId }), {
    onSuccess: () => {
      queryClient.invalidateQueries(["writing"]);
      queryClient.invalidateQueries(["writings"]);
    },
  });
