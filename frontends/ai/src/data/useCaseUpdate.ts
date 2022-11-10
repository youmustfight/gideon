import axios from "axios";
import { useMutation, useQuery } from "react-query";
import { getGideonApiUrl } from "../env";
import { queryClient } from "./queryClient";
import { TCase } from "./useCase";

const reqCasePut = async (cse: any): Promise<TCase> =>
  axios.put(`${getGideonApiUrl()}/v1/case/${cse.id}`, { case: cse }).then((res) => res.data.case);

export const useCaseUpdate = () =>
  useMutation(async (data: Partial<TCase>) => reqCasePut({ id: data.id, ...data }), {
    onSuccess: () => {
      queryClient.invalidateQueries(["case"]);
      queryClient.invalidateQueries(["cases"]);
    },
  });
