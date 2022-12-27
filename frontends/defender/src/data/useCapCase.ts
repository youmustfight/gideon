import axios from "axios";
import { useQuery } from "react-query";
import { getGideonApiUrl } from "../env";

export type TCapCase = {
  // CAP
  analysis: {
    char_count: number;
    ocr_confidence: number;
    word_count: number;
  };
  cap_id: number;
  casebody: {
    attorneys: string[];
    corrections: string;
    head_matter: string;
    judges: string[];
    opinions: { author: string; text: string; type: string }[];
    parties: string[];
  };
  cites_to: {
    case_ids: number[];
    category: string;
    cite: string;
    opinion_id: number;
    reporter: string;
    weight: number;
  }[];
  court: {
    id: number;
    name_abbreviation: string;
    slug: string;
    url: string;
  };
  jurisdiction: {
    name: string;
    name_long: string;
  };
  decision_date: string;
  docket_number: string;
  name: string;
  name_abbreviation: string;
  // GIDEON
  id: number;
  generated_citing_slavery_summary: string;
  generated_citing_slavery_summary_one_liner: string;
  generated_summary: string;
  generated_summary_one_liner: string;
};

// GET
const reqCapCaseGet = async (capId: number): Promise<TCapCase> => {
  return axios.get(`${getGideonApiUrl()}/v1/cap/case/${capId}`).then((res) => res.data.data.cap_case);
};

export const useCapCase = (capId: number) => {
  return useQuery<TCapCase | null>(["capCase", Number(capId)], async () => (capId ? reqCapCaseGet(capId) : null), {
    refetchInterval: 1000 * 60,
  });
};
