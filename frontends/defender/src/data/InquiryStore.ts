import createVanilla from "zustand/vanilla";
import create from "zustand";
import {
  reqQueryCaselaw,
  reqQueryDocument,
  reqQueryDocumentLocations,
  reqQueryLegalBriefFactSimilarity,
  reqQueryWritingSimilarity,
  TQueryLocation,
} from "./useQueryAI";
import { TCapCase } from "./useCapCase";

type TInquiryScope = "caselaw" | "organization" | "case" | "document";
type TFocusAnswer = "question" | "location" | "caseFacts" | "writingSimilarity" | "caselaw";

type TInquiryStore = {
  // scopes
  inquiryScope: TInquiryScope;
  setInquiryScope: (inquiryScope: TInquiryScope) => void;
  // inquiry + answers
  query: string;
  setQuery: (query: string) => void;
  answerQuestion?: {
    answer?: string;
    inProgress?: boolean;
    locations?: TQueryLocation[];
  };
  answerDetailsLocations?: {
    inProgress?: boolean;
    locations?: TQueryLocation[];
  };
  answerCaseFactsSimilarity?: {
    inProgress?: boolean;
    locations?: TQueryLocation[];
  };
  answerWritingSimilarity?: {
    inProgress?: boolean;
    locations?: TQueryLocation[];
  };
  answerCaselaw?: {
    inProgress?: boolean;
    capCases?: TCapCase[]; // TODO
  };
  inquiry: (params: any) => void;
  isInquirySubmitted: boolean;
  // after
  focusAnswer?: TFocusAnswer;
  setFocusAnswer: (focusAnswer: TFocusAnswer) => void;
  clearInquiry: () => void;
};

export const inquiryStore = createVanilla<TInquiryStore>((set, get) => ({
  // setup
  inquiryScope: "organization",
  setInquiryScope: (inquiryScope) => set({ inquiryScope }),
  // inquiry
  query: "",
  setQuery: (query) => set({ query }),
  isInquirySubmitted: false,
  answerQuestion: undefined,
  answerDetailsLocations: undefined,
  answerCaseFactsSimilarity: undefined,
  answerWritingSimilarity: undefined,
  answerCaselaw: undefined,
  inquiry: ({ caseId, documentId, organizationId }) => {
    set({ isInquirySubmitted: true });

    // ORG
    if (get().inquiryScope === "organization") {
      // --- case facts (defer to case id if that's provided over query)
      set({ answerCaseFactsSimilarity: { inProgress: true } });
      if (caseId) {
        reqQueryLegalBriefFactSimilarity({ caseId, organizationId }).then(({ locations }) =>
          set({
            answerCaseFactsSimilarity: { inProgress: false, locations },
            query: `Case facts similar to case #${caseId}`,
          })
        );
      } else {
        reqQueryLegalBriefFactSimilarity({ organizationId, query: get().query }).then(({ locations }) =>
          set({ answerCaseFactsSimilarity: { inProgress: false, locations } })
        );
      }
      // --- writing (skip if provided caseId)
      if (!caseId) {
        set({ answerWritingSimilarity: { inProgress: true } });
        reqQueryWritingSimilarity({ organizationId, query: get().query }).then(({ locations }) =>
          set({ answerWritingSimilarity: { inProgress: false, locations } })
        );
      } else {
        set({ answerWritingSimilarity: { inProgress: false, locations: [] } });
      }
      set({ focusAnswer: "caseFacts" });

      // CASE
    } else if (get().inquiryScope === "case") {
      // --- detail
      set({ answerDetailsLocations: { inProgress: true } });
      reqQueryDocumentLocations({ caseId, query: get().query }).then(({ locations }) =>
        set({ answerDetailsLocations: { inProgress: false, locations } })
      );
      // --- answer
      set({ answerQuestion: { inProgress: true } });
      reqQueryDocument({
        caseId,
        query: get().query,
      }).then(({ answer, locations }) => set({ answerQuestion: { answer, locations } }));
      set({ focusAnswer: "location" });

      // DOCUMENT
    } else if (get().inquiryScope === "document") {
      // --- detail
      set({ answerDetailsLocations: { inProgress: true } });
      reqQueryDocumentLocations({
        caseId,
        documentId,
        query: get().query,
      }).then(({ locations }) => set({ answerDetailsLocations: { locations } }));
      //} --- answer
      set({ answerQuestion: { inProgress: true } });
      reqQueryDocument({
        caseId,
        documentId,
        query: get().query,
      }).then(({ answer, locations }) => set({ answerQuestion: { answer, locations } }));
      // set default focus
      set({ focusAnswer: "location" });

      // CASELAW
    } else if (get().inquiryScope === "caselaw") {
      set({ answerCaselaw: { inProgress: true } });
      reqQueryCaselaw({ query: get().query }).then(({ capCases }) =>
        set({ answerCaselaw: { inProgress: false, capCases } })
      );
      set({ focusAnswer: "caselaw" });
    }
  },
  // after
  focusAnswer: undefined,
  setFocusAnswer: (focusAnswer) => set({ focusAnswer }),
  clearInquiry: () =>
    set({
      answerQuestion: undefined,
      answerDetailsLocations: undefined,
      answerCaseFactsSimilarity: undefined,
      answerWritingSimilarity: undefined,
      answerCaselaw: undefined,
      isInquirySubmitted: false,
      focusAnswer: undefined,
      query: "",
    }),
}));

export const useInquiryStore = create(inquiryStore);
