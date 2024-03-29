import createVanilla from "zustand/vanilla";
import create from "zustand";
import {
  LOCAL_STORAGE_KEY_FOCUSED_CASE_ID,
  LOCAL_STORAGE_KEY_FOCUSED_DOCUMENT_ID,
  LOCAL_STORAGE_KEY_FOCUSED_ORG_ID,
} from "./localStorageKeys";

type TAppStore = {
  focusedCaseId?: number;
  focusedDocumentId?: number;
  focusedOrgId?: number;
  setFocusedCaseId: (focusedCaseId?: number) => void;
  setFocusedDocumentId: (focusedDocumentId?: number) => void;
  setFocusedOrgId: (focusedOrgId?: number) => void;
};

export const appStore = createVanilla<TAppStore>((set, get) => ({
  focusedCaseId: localStorage.getItem(LOCAL_STORAGE_KEY_FOCUSED_CASE_ID)
    ? Number(localStorage.getItem(LOCAL_STORAGE_KEY_FOCUSED_CASE_ID))
    : undefined,
  focusedDocumentId: localStorage.getItem(LOCAL_STORAGE_KEY_FOCUSED_DOCUMENT_ID)
    ? Number(localStorage.getItem(LOCAL_STORAGE_KEY_FOCUSED_DOCUMENT_ID))
    : undefined,
  focusedOrgId: localStorage.getItem(LOCAL_STORAGE_KEY_FOCUSED_ORG_ID)
    ? Number(localStorage.getItem(LOCAL_STORAGE_KEY_FOCUSED_ORG_ID))
    : undefined,
  setFocusedCaseId: (focusedCaseId) => {
    set({ focusedCaseId });
    if (focusedCaseId) {
      localStorage.setItem(LOCAL_STORAGE_KEY_FOCUSED_CASE_ID, String(focusedCaseId));
    } else {
      localStorage.removeItem(LOCAL_STORAGE_KEY_FOCUSED_CASE_ID);
    }
  },
  setFocusedDocumentId: (focusedDocumentId) => {
    set({ focusedDocumentId });
    if (focusedDocumentId) {
      localStorage.setItem(LOCAL_STORAGE_KEY_FOCUSED_DOCUMENT_ID, String(focusedDocumentId));
    } else {
      localStorage.removeItem(LOCAL_STORAGE_KEY_FOCUSED_DOCUMENT_ID);
    }
  },
  setFocusedOrgId: (focusedOrgId) => {
    set({ focusedOrgId });
    if (focusedOrgId) {
      localStorage.setItem(LOCAL_STORAGE_KEY_FOCUSED_ORG_ID, String(focusedOrgId));
    } else {
      localStorage.removeItem(LOCAL_STORAGE_KEY_FOCUSED_ORG_ID);
    }
  },
}));

export const useAppStore = create(appStore);
