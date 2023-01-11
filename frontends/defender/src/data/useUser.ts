import axios from "axios";
import { useMutation, useQuery } from "react-query";
import * as Env from "../env";
import { LOCAL_STORAGE_KEY_API_TOKEN } from "./localStorageKeys";
import { queryClient } from "./queryClient";

export type TUser = {
  id: number;
  name?: string;
  email?: string;
  password?: string;
};

// GET
const reqUserGet = async (): Promise<TUser | null> =>
  axios.get(`${Env.getGideonApiUrl()}/v1/auth/user`).then((res) => res.data.user);

export const useUser = () => {
  return useQuery<TUser | null>(["user"], async () => reqUserGet(), {
    refetchInterval: 1000 * 60,
  });
};

// UPDATE
const reqUserPut = async (user: any): Promise<TUser> =>
  axios.put(`${Env.getGideonApiUrl()}/v1/user/${user.id}`, { user }).then(() => {
    // TODO
    return user;
  });

export const useUserUpdate = () =>
  useMutation(async (data: Partial<TUser>) => reqUserPut({ id: data.id, ...data }), {
    onSuccess: () => {
      // TODO
    },
  });

// AUTH - LOGIN
export type TUserLoginParams = {
  email: string;
  password: string;
};

const reqUserLogin = async ({ email, password }: TUserLoginParams): Promise<{ token: string; user: TUser }> =>
  await axios.post(`${Env.getGideonApiUrl()}/v1/auth/login`, { email, password }).then((req) => req.data);

export const useUserLogin = () =>
  useMutation(
    async ({ email, password }: TUserLoginParams): Promise<TUser | null> => {
      try {
        const { token, user } = await reqUserLogin({ email, password });
        localStorage.setItem(LOCAL_STORAGE_KEY_API_TOKEN, token);
        return user;
      } catch (err: any) {
        // grab server response err text first, then see if it's JS error
        throw err.response?.data?.message ?? err.message;
      }
    },
    {
      mutationKey: ["user"],
      onSuccess: (user) => {
        if (user) queryClient.setQueryData(["user"], user);
      },
    }
  );

// AUTH - LOGOUT
export const useUserLogout = () => {
  return useMutation(async () => console.log("Unnecessary atm"), {
    onSettled: async () => {
      localStorage.removeItem(LOCAL_STORAGE_KEY_API_TOKEN);
      location.reload();
    },
  });
};

// MISC
export const reqUserAILocksReset = async (userId: number): Promise<void> => {
  return axios.put(`${Env.getGideonApiUrl()}/v1/user/${userId}/ai_action_locks_reset`);
};
