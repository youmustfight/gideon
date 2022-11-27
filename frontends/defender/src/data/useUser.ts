import axios from "axios";
import { useQuery } from "react-query";
import * as Env from "../env";

export type TUser = {
  id: number;
  name?: string;
  email?: string;
};

// USER FETCH
const reqUserGet = async (): Promise<TUser | null> =>
  axios.get(`${Env.getGideonApiUrl()}/v1/auth/user`).then((res) => res.data.user);

export const useUser = () => {
  return useQuery<TUser | null>(["user"], async () => reqUserGet(), {
    refetchInterval: 1000 * 60,
  });
};
