import axios from "axios";
import { useQuery } from "react-query";
import { getGideonApiUrl } from "../env";
import { TWriting } from "./useWritings";

// Filters for user via forUser
const reqWritingGet = async (writingId: number | string): Promise<TWriting> =>
  axios.get(`${getGideonApiUrl()}/v1/writing/${writingId}`).then((res) => res.data.writing);

export const useWriting = (writingId: number | string) => {
  return useQuery<TWriting>(["writing", writingId], async () => reqWritingGet(writingId), {
    refetchInterval: 1000 * 60,
  });
};
