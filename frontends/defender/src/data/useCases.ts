import axios from "axios";
import { useQuery } from "react-query";
import { getGideonApiUrl } from "../env";
import { TCase } from "./useCase";

type TUseCasesParams = {
  organizationId?: number;
};

const reqCasesGet = async (params: TUseCasesParams): Promise<TCase[]> => {
  return axios
    .get(`${getGideonApiUrl()}/v1/cases`, { params: { organization_id: params.organizationId } })
    .then((res) => res.data.data.cases);
};

export const useCases = (params: TUseCasesParams) => {
  return useQuery<TCase[]>(["cases"], async () => reqCasesGet(params), {
    refetchInterval: 1000 * 60 * 5,
    enabled: params.organizationId != null,
  });
};
