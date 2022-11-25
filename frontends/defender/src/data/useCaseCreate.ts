import axios from "axios";
import { useMutation, useQuery } from "react-query";
import { getGideonApiUrl } from "../env";
import { queryClient } from "./queryClient";

const reqCasePost = async ({ userId }: any): Promise<any> =>
  axios.post(`${getGideonApiUrl()}/v1/case`, { userId }).then((res) => res.data.case);

export const useCaseCreate = () =>
  useMutation(async ({ userId }: { userId: number }) => reqCasePost({ userId }), {
    onSuccess: () => {
      queryClient.invalidateQueries(["case"]);
      queryClient.invalidateQueries(["cases"]);
    },
  });
