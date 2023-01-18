import axios from "axios";
import { useQuery } from "react-query";
import { getGideonApiUrl } from "../env";

export type TWriting = {
  id: number;
  case_id: number;
  document_id: number;
  name: string;
  body_html: string;
  body_text: string;
  is_template: boolean;
};

type TWritingFilterParams = {
  caseId?: number;
  documentId?: number;
  isTemplate?: boolean;
  organizationId?: number;
};

// Filters for user via forUser
const reqWritingsGet = async ({
  caseId,
  documentId,
  isTemplate,
  organizationId,
}: TWritingFilterParams): Promise<TWriting[]> =>
  axios
    .get(`${getGideonApiUrl()}/v1/writings`, {
      params: { case_id: caseId, document_id: documentId, is_template: isTemplate, organization_id: organizationId },
    })
    .then((res) => res.data?.data?.writings);

export const useWritings = (params: TWritingFilterParams) => {
  return useQuery<TWriting[]>(["writings", JSON.stringify(params)], async () => reqWritingsGet(params), {
    refetchInterval: 1000 * 15,
  });
};
