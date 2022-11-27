import axios from "axios";
import { useMutation } from "react-query";
import { LOCAL_STORAGE_KEY_API_TOKEN } from "./axiosConfig";
import { getGideonApiUrl } from "../env";
import { queryClient } from "./queryClient";
import { TUser } from "./useUser";

export type TUserLoginParams = {
  email: string;
  password: string;
};

// USER AUTH
const reqUserLogin = async ({ email, password }: TUserLoginParams): Promise<{ token: string; user: TUser }> =>
  await axios.post(`${getGideonApiUrl()}/v1/auth/login`, { email, password }).then((req) => req.data);

export const useUserLogin = () =>
  useMutation(
    async ({ email, password }: TUserLoginParams): Promise<TUser | null> => {
      try {
        const { token, user } = await reqUserLogin({ email, password });
        localStorage.setItem(LOCAL_STORAGE_KEY_API_TOKEN, token);
        return user;
      } catch (err) {
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
