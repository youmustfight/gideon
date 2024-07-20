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
import { reqWritingDocumentMemo, reqWritingTemplate } from "../../data/useWriting";

export type TAIRequestType = "inquiry" | "summarize" | "write";
export type TWritingScope = "templateCase" | "templatePrompt" | "memoDocument";
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
  // --- scroll focus
  isScrollingToAIRequestBox: boolean;
  scrollToAIRequestBox: () => void;
  // --- clearing/reset
  clearAIRequest: () => void;

  // INQUIRY
  // --- setup
  inquiryScope: TInquiryScope;
  setInquiryScope: (inquiryScope: TInquiryScope) => void;
  // --- query & answers
  inquiryQuery: string;
  setInquiryQuery: (inquiryQuery: string) => void;
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
  setSummaryInput: (summaryInput: Partial<TUseBriefCreateBody> & { text: string }) => void;
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
    promptText: string;
    writingTemplateId?: number | string;
    writingModel?: Partial<TWriting>;
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
    writing?: TWriting | Partial<TWriting>;
  };
  setAnswerWriting: (writing: TWriting) => void;
};

export const aiRequestStore = createVanilla<TAIRequestStore>((set, get) => ({
  // GLOBAL
  aiRequestType: "inquiry",
  setAIRequestType: (aiRequestType) => set({ aiRequestType }),
  // --- post-answer
  isAIRequestSubmitted: false,
  focusAnswer: undefined,
  setFocusAnswer: (focusAnswer) => set({ focusAnswer }),
  // --- scroll focus
  isScrollingToAIRequestBox: false,
  scrollToAIRequestBox: () => {
    set({ isScrollingToAIRequestBox: true });
    // @ts-ignore
    const el = document.inquiryQuerySelector("#ai-request-box");
    if (el) {
      // el.scrollIntoView({ behavior: "smooth" });
      window.scrollTo(0, 0);
      setTimeout(() => {
        set({ isScrollingToAIRequestBox: false });
      }, 1000 * 3);
    }
  },
  // --- clearing/reset
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
      inquiryQuery: "",
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
  inquiryQuery: "",
  setInquiryQuery: (inquiryQuery) => set({ inquiryQuery }),
  answerQuestion: undefined,
  answerDetailsLocations: undefined,
  answerCaseFactsSimilarity: undefined,
  answerWritingSimilarity: undefined,
  answerCaselaw: undefined,
  inquiry: ({ caseId, documentId, organizationId, userId }) => {
    set({ isAIRequestSubmitted: true });
    // ORG
    if (get().inquiryScope === "organization") {
      // --- case facts (defer to case id if that's provided over query)
      set({ answerCaseFactsSimilarity: { inProgress: true } });
      if (caseId) {
        reqQueryBriefFactSimilarity({ caseId, organizationId }).then(({ locations }) =>
          set({
            answerCaseFactsSimilarity: { inProgress: false, locations },
            inquiryQuery: `Case facts similar to case #${caseId}`,
          })
        );
      } else {
        reqQueryBriefFactSimilarity({ organizationId, query: get().inquiryQuery }).then(({ locations }) =>
          set({ answerCaseFactsSimilarity: { inProgress: false, locations } })
        );
      }
      // --- writing (skip if provided caseId)
      if (!caseId) {
        set({ answerWritingSimilarity: { inProgress: true } });
        reqQueryWritingSimilarity({ organizationId, query: get().inquiryQuery }).then(({ locations }) =>
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
      reqQueryDocumentLocations({ caseId, query: get().inquiryQuery }).then(({ locations }) =>
        set({ answerDetailsLocations: { inProgress: false, locations } })
      );
      // --- answer
      set({ answerQuestion: { inProgress: true } });
      setTimeout(
        () =>
          reqQueryDocument({
            caseId,
            query: get().inquiryQuery,
          }).then(({ answer, locations }) => set({ answerQuestion: { answer, locations, inProgress: false } })),
        500
      );
      set({ focusAnswer: "question" });

      // DOCUMENT
    } else if (get().inquiryScope === "document") {
      // --- detail
      set({ answerDetailsLocations: { inProgress: true } });
      reqQueryDocumentLocations({
        caseId,
        documentId,
        query: get().inquiryQuery,
        userId,
      }).then(({ locations }) => set({ answerDetailsLocations: { locations, inProgress: false } }));
      //} --- answer
      set({ answerQuestion: { inProgress: true } });
      setTimeout(
        () =>
          reqQueryDocument({
            caseId,
            documentId,
            query: get().inquiryQuery,
            userId,
          }).then(({ answer, locations }) => set({ answerQuestion: { answer, locations, inProgress: false } })),
        500
      );
      // set default focus
      set({ focusAnswer: "location" });
      // CASELAW
    } else if (get().inquiryScope === "caselaw") {
      set({ answerCaselaw: { inProgress: true } });
      reqQueryCaselaw({ query: get().inquiryQuery }).then(({ capCases }) =>
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
  summarize: ({ caseId, documentId, userId }) => {
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
  write: ({ caseId, documentId, organizationId, userId }) => {
    set({ isAIRequestSubmitted: true, answerWriting: { inProgress: true } });
    const { promptText, writingTemplateId, writingModel } = get().writingInput;
    // MEMOS
    if (get().writingScope === "memoDocument") {
      reqWritingDocumentMemo({ documentId, promptText, userId }).then((writing) =>
        set({ answerWriting: { inProgress: false, writing } })
      );
      // TEMPLATE FILLS
    } else if (["templateCase", "templatePrompt"].includes(get().writingScope ?? "")) {
      reqWritingTemplate(
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
    }
  },
  // --- answers
  answerWriting: undefined,
  setAnswerWriting: (writing) => set({ isAIRequestSubmitted: true, answerWriting: { inProgress: false, writing } }),
}));

export const useAIRequestStore = create(aiRequestStore);
