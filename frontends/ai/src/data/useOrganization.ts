import axios from "axios";
import { useQuery } from "react-query";
import { getGideonApiUrl } from "../env";

export type TOrganization = {
  id: number;
  name?: string;
};

// Filters for user via forOrgnaization
const reqOrganizationsGet = async (): Promise<TOrganization[]> =>
  // HACK: manually setting a fetch until setting up auth
  axios.get(`${getGideonApiUrl()}/v1/organizations`).then((res) => res.data.organizations);

export const useOrgnaizations = () => {
  return useQuery<TOrganization[]>(["organizations"], async () => reqOrganizationsGet(), {
    refetchInterval: 1000 * 60 * 15,
  });
};
