import axios from "axios";
import createVanilla from "zustand/vanilla";
import create from "zustand";
import { TDocumentHighlight } from "./useHighlights";

type THighlightStore = {
  sentenceStartIndex: number | null;
  setSentenceStartIndex: (index: number | null) => void;
  sentenceEndIndex: number | null;
  setSentenceEndIndex: (index: number | null) => void;
  highlightNoteSubmitted: boolean;
  hightlightNoteText: string;
  setHightlightNoteText: (string: string) => void;
  saveHighlightAndOpinion: (payload: TDocumentHighlight) => void;
};

export const highlightStore = createVanilla<THighlightStore>((set, get) => ({
  // Selecting
  sentenceStartIndex: null,
  sentenceEndIndex: null,
  setSentenceStartIndex: (sentenceStartIndex) => set({ sentenceStartIndex }),
  setSentenceEndIndex: (sentenceEndIndex) => set({ sentenceEndIndex }),
  // Editing
  highlightNoteSubmitted: false,
  hightlightNoteText: "",
  setHightlightNoteText: (hightlightNoteText) => set({ hightlightNoteText }),
  saveHighlightAndOpinion: async (payload) => {
    set({ highlightNoteSubmitted: true });
    await axios.post("http://localhost:3000/highlights", { highlight: payload });
    set({ highlightNoteSubmitted: false, hightlightNoteText: "", sentenceStartIndex: null, sentenceEndIndex: null });
  },
}));

export const useHighlightStore = create(highlightStore);
