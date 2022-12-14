import axios from "axios";
import { useMutation, useQuery } from "react-query";
import { getGideonApiUrl } from "../env";
import { queryClient } from "./queryClient";
import { TWriting } from "./useWritings";

const reqWritingPut = async (writing: any): Promise<TWriting> =>
  axios.put(`${getGideonApiUrl()}/v1/writing/${writing.id}`, { writing: writing }).then((res) => res.data.writing);

export const useWritingUpdate = () =>
  useMutation(async (data: Partial<TWriting>) => reqWritingPut({ id: data.id, ...data }), {
    onSuccess: () => {
      queryClient.invalidateQueries(["writing"]);
      queryClient.invalidateQueries(["writings"]);
    },
  });
