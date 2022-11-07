import axios from "axios";
import { useQuery } from "react-query";
import { getGideonApiUrl } from "../env";

export type TCase = {
  id: number;
};

const reqCaseGet = async (caseId: number): Promise<TCase> => {
  return axios.get(`${getGideonApiUrl()}/v1/case/${caseId}`).then((res) => res.data.case);
};

export const useCase = (caseId: number) => {
  return useQuery<TCase>(["case", caseId], async () => reqCaseGet(caseId), {
    refetchInterval: 1000 * 60,
  });
};
