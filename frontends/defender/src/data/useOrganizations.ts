import axios from "axios";
import { useMutation, useQuery } from "react-query";
import { getGideonApiUrl } from "../env";
import { TUser } from "./useUser";

export type TOrganization = {
  id: number;
  name?: string;
  users?: TUser[];
};

// Filters for user via forOrgnaization
const reqOrganizationsGet = async (): Promise<TOrganization[]> =>
  // HACK: manually setting a fetch until setting up auth
  axios.get(`${getGideonApiUrl()}/v1/organizations`).then((res) => res.data.data.organizations);

export const useOrganizations = () => {
  return useQuery<TOrganization[]>(["organizations"], async () => reqOrganizationsGet(), {
    refetchInterval: 1000 * 60 * 15,
  });
};

// USER UPDATE
type TUseOrganizationUserParams = {
  action: "add" | "remove";
  organization_id: number;
  user_id?: number;
  user?: TUser;
};

const reqOrganizationUserPost = async (params: TUseOrganizationUserParams): Promise<TUser> =>
  axios.post(`${getGideonApiUrl()}/v1/organization/${params.organization_id}/user`, params);

export const useOrganizationUserUpdate = () =>
  useMutation(async (data: TUseOrganizationUserParams) => reqOrganizationUserPost(data), {
    onSuccess: () => {
      // TODO
    },
  });
