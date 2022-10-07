import axios from "axios";
import { useQuery } from "react-query";

export type TUser = {
  id: number;
  name?: string;
};

// Filters for user via forUser
const reqUsersGet = async (): Promise<TUser[]> =>
  axios.get("http://localhost:3000/users").then((res) => res.data.users);

export const useUsers = () => {
  return useQuery<TUser[]>(["users"], async () => reqUsersGet(), {
    refetchInterval: 1000 * 60 * 15,
  });
};
