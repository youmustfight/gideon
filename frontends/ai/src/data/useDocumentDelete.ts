import axios from "axios";
import { getGideonApiUrl } from "../env";

// Filters for user via forUser
export const reqDocumentDelete = async (documentId: number | string): Promise<void> =>
  axios.delete(`${getGideonApiUrl()}/v1/document/${documentId}`);
