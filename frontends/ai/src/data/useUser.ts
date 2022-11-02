import axios from "axios";
import { useMutation, useQuery } from "react-query";
import { getGideonApiUrl } from "../env";
import { queryClient } from "./queryClient";

export type TUser = {
  id: number;
  name?: string;
};

export type TUserLoginParams = {
  email: string;
  password: string;
};

// USER AUTH
const reqUserLogin = async ({ email, password }: TUserLoginParams): Promise<void> =>
  await axios.post(`${getGideonApiUrl()}/v1/auth/login`, { email, password }).then((req) => req.data.user);

export const useUserLogin = () =>
  useMutation(async ({ email, password }: TUserLoginParams): Promise<void> => reqUserLogin({ email, password }), {
    mutationKey: ["user"],
    onSuccess: (user) => {
      queryClient.setQueryData(["user"], user);
    },
  });

// USER FETCH
// --- filters for user via forUser
const reqUserGet = async (): Promise<TUser | null> => {
  // HACK: manually setting a fetch until setting up auth
  const userId = queryClient.getQueryData(["user"])?.id;
  if (!userId) return null;
  // --- fetch
  const user = await axios.get(`${getGideonApiUrl()}/v1/user/${userId}`).then((res) => res.data.user);
  // --- return
  return user;
};

export const useUser = () => {
  return useQuery<TUser | null>(["user"], async () => reqUserGet(), {
    refetchInterval: 1000 * 60,
  });
};
