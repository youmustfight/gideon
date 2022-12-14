import axios from "axios";
import { getGideonApiUrl } from "../env";

// Filters for user via forUser
export const reqWritingDelete = async (writingId: number | string): Promise<void> =>
  axios.delete(`${getGideonApiUrl()}/v1/writing/${writingId}`);
