import axios from "axios";
import { useQuery } from "react-query";
import { getGideonApiUrl } from "../env";
import { TCase } from "./useCase";

type TUseCasesParams = {
  userId?: number;
};

const reqCasesGet = async (params: TUseCasesParams): Promise<TCase[]> => {
  return axios.get(`${getGideonApiUrl()}/v1/cases`, { params }).then((res) => res.data.cases);
};

export const useCases = (params: TUseCasesParams) => {
  return useQuery<TCase[]>(["cases"], async () => reqCasesGet(params), {
    refetchInterval: 1000 * 60 * 5,
  });
};
