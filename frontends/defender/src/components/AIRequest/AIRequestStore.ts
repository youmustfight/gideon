import createVanilla from "zustand/vanilla";
import create from "zustand";
import {
  TQueryLocation,
  reqQueryCaselaw,
  reqQueryDocument,
  reqQueryDocumentLocations,
  reqQueryBriefFactSimilarity,
  reqQueryWritingSimilarity,
  reqQuerySummarize,
} from "./aiRequestReqs";
import { TCapCase } from "../../data/useCapCase";
import { reqBriefCreate, TUseBriefCreateBody } from "../../data/useBrief";
import { reqDocumentSummarize } from "../../data/useDocument";
import { TWriting } from "../../data/useWritings";
import { reqWritingPost } from "../../data/useWriting";

export type TAIRequestType = "inquiry" | "summarize" | "write";
export type TWritingScope = "case" | "prompt";
export type TSummaryScope = "case" | "document" | "text";
export type TInquiryScope = "caselaw" | "organization" | "case" | "document";
export type TFocusAnswer = "question" | "location" | "caseFacts" | "writingSimilarity" | "caselaw";

type TAIRequestStore = {
  // GLOBAL
  aiRequestType: TAIRequestType;
  setAIRequestType: (aiRequestType: TAIRequestType) => void;
  // --- post-answer
  isAIRequestSubmitted: boolean;
  focusAnswer?: TFocusAnswer;
  setFocusAnswer: (focusAnswer: TFocusAnswer) => void;
  clearAIRequest: () => void;

  // INQUIRY
  // --- setup
  inquiryScope: TInquiryScope;
  setInquiryScope: (inquiryScope: TInquiryScope) => void;
  // --- query & answers
  query: string;
  setQuery: (query: string) => void;
  answerQuestion?: {
    answer?: string;
    inProgress: boolean;
    locations?: TQueryLocation[];
  };
  answerDetailsLocations?: {
    inProgress: boolean;
    locations?: TQueryLocation[];
  };
  answerCaseFactsSimilarity?: {
    inProgress: boolean;
    locations?: TQueryLocation[];
  };
  answerWritingSimilarity?: {
    inProgress: boolean;
    locations?: TQueryLocation[];
  };
  answerCaselaw?: {
    inProgress: boolean;
    capCases?: TCapCase[]; // TODO
  };
  inquiry: (params: any) => void;

  // SUMMARIZE
  summaryScope?: TSummaryScope;
  setSummaryScope: (summaryScope: TSummaryScope) => void;
  summaryInput: Partial<TUseBriefCreateBody> & { text: string };
  setSummaryInput: (query: Partial<TUseBriefCreateBody> & { text: string }) => void;
  // --- query
  summarize: (params: any) => void;
  // --- answers
  answerSummary?: {
    inProgress: boolean;
    summary?: string;
  };

  // WRITING
  writingScope?: TWritingScope;
  setWritingScope: (writingScope: TWritingScope) => void;
  writingInput: {
    writingTemplateId?: number | string;
    writingModel?: Partial<TWriting>;
    promptText: string;
  };
  setWritingInput: (input: {
    writingTemplateId?: number | string;
    writingModel?: Partial<TWriting>;
    promptText: string;
  }) => void;
  // --- query
  write: (params: any) => void;
  // --- answers
  answerWriting?: {
    inProgress: boolean;
    writing?: TWriting;
  };
};

export const aiRequestStore = createVanilla<TAIRequestStore>((set, get) => ({
  // GLOBAL
  aiRequestType: "inquiry",
  setAIRequestType: (aiRequestType) => set({ aiRequestType }),
  // --- post-answer
  focusAnswer: undefined,
  setFocusAnswer: (focusAnswer) => set({ focusAnswer }),
  clearAIRequest: () =>
    set({
      // --- answers
      answerCaseFactsSimilarity: undefined,
      answerCaselaw: undefined,
      answerDetailsLocations: undefined,
      answerQuestion: undefined,
      answerSummary: undefined,
      answerWritingSimilarity: undefined,
      answerWriting: undefined,
      // --- inputs
      query: "",
      summaryInput: { text: "", issues: [] },
      writingInput: { promptText: "", writingTemplateId: undefined, writingModel: undefined },
      // --- meta
      isAIRequestSubmitted: false,
      focusAnswer: undefined,
    }),

  // INQUIRY
  // --- setup
  inquiryScope: "organization",
  setInquiryScope: (inquiryScope) => set({ inquiryScope }),
  // --- query & answers
  query: "",
  setQuery: (query) => set({ query }),
  isAIRequestSubmitted: false,
  answerQuestion: undefined,
  answerDetailsLocations: undefined,
  answerCaseFactsSimilarity: undefined,
  answerWritingSimilarity: undefined,
  answerCaselaw: undefined,
  inquiry: ({ caseId, documentId, organizationId }) => {
    set({ isAIRequestSubmitted: true });
    // ORG
    if (get().inquiryScope === "organization") {
      // --- case facts (defer to case id if that's provided over query)
      set({ answerCaseFactsSimilarity: { inProgress: true } });
      if (caseId) {
        reqQueryBriefFactSimilarity({ caseId, organizationId }).then(({ locations }) =>
          set({
            answerCaseFactsSimilarity: { inProgress: false, locations },
            query: `Case facts similar to case #${caseId}`,
          })
        );
      } else {
        reqQueryBriefFactSimilarity({ organizationId, query: get().query }).then(({ locations }) =>
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
      }).then(({ answer, locations }) => set({ answerQuestion: { answer, locations, inProgress: false } }));
      set({ focusAnswer: "location" });
      // DOCUMENT
    } else if (get().inquiryScope === "document") {
      // --- detail
      set({ answerDetailsLocations: { inProgress: true } });
      reqQueryDocumentLocations({
        caseId,
        documentId,
        query: get().query,
      }).then(({ locations }) => set({ answerDetailsLocations: { locations, inProgress: false } }));
      //} --- answer
      set({ answerQuestion: { inProgress: true } });
      reqQueryDocument({
        caseId,
        documentId,
        query: get().query,
      }).then(({ answer, locations }) => set({ answerQuestion: { answer, locations, inProgress: false } }));
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

  // SUMMARIZE
  summaryScope: undefined,
  setSummaryScope: (summaryScope) => set({ summaryScope, summaryInput: { text: "", issues: [] } }),
  // --- inputs
  summaryInput: { text: "", issues: [] },
  setSummaryInput: (summaryInput) => set({ summaryInput }),
  // --- query
  summarize: ({ caseId, documentId }) => {
    set({ isAIRequestSubmitted: true, answerSummary: { inProgress: true } });
    // TEXT
    if (get().summaryScope === "text") {
      reqQuerySummarize({ text: get().summaryInput.text }).then(({ summary }) =>
        set({ answerSummary: { inProgress: false, summary } })
      );
    }
    // CASE
    if (get().summaryScope === "case") {
      reqBriefCreate({ caseId, issues: get().summaryInput?.issues }).then(() =>
        // long running process so don't set inProgress = false
        set({ answerSummary: { inProgress: true } })
      );
    }
    // DOCUMENT
    if (get().summaryScope === "document") {
      // TODO: this function is always going to re-run summarization even if its present
      reqDocumentSummarize(documentId).then((document) =>
        // TODO: return string from document extraction/summarization job
        set({ answerSummary: { inProgress: false, summary: document.generated_summary } })
      );
    }
  },
  // --- answers
  answerSummary: undefined,

  // WRITING
  writingScope: undefined,
  setWritingScope: (writingScope) => set({ writingScope, writingInput: { ...get().writingInput, promptText: "" } }),
  // --- inputs
  writingInput: { writingTemplateId: undefined, writingModel: undefined, promptText: "" },
  setWritingInput: (writingInput) => set({ writingInput }),
  // --- query
  write: ({ caseId, organizationId }) => {
    set({ isAIRequestSubmitted: true, answerWriting: { inProgress: true } });
    const { promptText, writingTemplateId, writingModel } = get().writingInput;
    reqWritingPost(
      {
        caseId: Number(caseId),
        isTemplate: false,
        name: writingModel!.name,
        organizationId,
        forkedWritingId: Number(writingTemplateId),
        bodyHtml: writingModel!.body_html,
        bodyText: writingModel!.body_text,
      },
      { runAIWriter: true, promptText }
    ).then((writing) => set({ answerWriting: { inProgress: false, writing } }));
  },
  // --- answers
  answerWriting: undefined,
}));

export const useAIRequestStore = create(aiRequestStore);
