import { useMutation } from "react-query";
import { LOCAL_STORAGE_KEY_API_TOKEN } from "./axiosConfig";

export const useUserLogout = () => {
  return useMutation(async () => console.log("Unnecessary atm"), {
    onSettled: async () => {
      localStorage.removeItem(LOCAL_STORAGE_KEY_API_TOKEN);
      location.reload();
    },
  });
};
