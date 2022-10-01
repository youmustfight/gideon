import axios from "axios";
import { useQuery } from "react-query";

export type TDocumentHighlight = {
  filename: string;
  user: string;
  document_text_vectors_by_sentence_start_index: number;
  document_text_vectors_by_sentence_end_index: number;
  highlight_text: string;
  highlight_text_vector?: number[];
  note_text: string;
  note_text_vector?: number[];
  // --- appended when searching/similaritiy
  highlight_score?: number;
  note_score?: number;
  score?: number;
};

// Filters for user via forUser
const reqHighlightsGet = async (): Promise<TDocumentHighlight[]> =>
  axios.get("http://localhost:3000/highlights").then((res) => res.data.highlights);

export const useHighlights = () => {
  return useQuery<TDocumentHighlight[]>(["highlights"], async () => reqHighlightsGet(), {
    refetchInterval: 1000 * 4,
  });
};
