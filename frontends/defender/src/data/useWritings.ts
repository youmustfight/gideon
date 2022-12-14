import axios from "axios";
import { useQuery } from "react-query";
import { getGideonApiUrl } from "../env";

export type TWriting = {
  id: number;
  case_id: number;
  name: string;
  body_html: string;
  body_text: string;
};

// Filters for user via forUser
const reqWritingsGet = async (caseId: number): Promise<TWriting[]> =>
  axios.get(`${getGideonApiUrl()}/v1/writings`, { params: { case_id: caseId } }).then((res) => res.data.data.writings);

export const useWritings = (caseId: number) => {
  return useQuery<TWriting[]>(["writings"], async () => reqWritingsGet(caseId), {
    refetchInterval: 1000 * 15,
  });
};
