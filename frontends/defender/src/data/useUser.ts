import axios from "axios";
import { useMutation, useQuery } from "react-query";
import { getGideonApiUrl } from "../env";
import { queryClient } from "./queryClient";

export type TUser = {
  id: number;
  name?: string;
  email?: string;
};

// USER FETCH
const reqUserGet = async (): Promise<TUser | null> =>
  axios.get(`${getGideonApiUrl()}/v1/auth/user`).then((res) => res.data.user);

export const useUser = () => {
  return useQuery<TUser | null>(["user"], async () => reqUserGet(), {
    refetchInterval: 1000 * 60,
  });
};
