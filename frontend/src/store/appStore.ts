import { create } from 'zustand';
import {
  JDParseResult,
  ResumeParseResult,
  ScreeningResult,
  QuestionGenerationResult,
  EvaluationResult,
  RiskDetectionResult,
  MultiAgentResult,
} from '@/types';

interface AppState {
  jd: JDParseResult | null;
  resume: ResumeParseResult | null;
  screeningResult: ScreeningResult | null;
  questions: QuestionGenerationResult | null;
  evaluation: EvaluationResult | null;
  risks: RiskDetectionResult | null;
  multiAgentResult: MultiAgentResult | null;

  setJD: (jd: JDParseResult) => void;
  setResume: (resume: ResumeParseResult) => void;
  setScreeningResult: (result: ScreeningResult) => void;
  setQuestions: (questions: QuestionGenerationResult) => void;
  setEvaluation: (evaluation: EvaluationResult) => void;
  setRisks: (risks: RiskDetectionResult) => void;
  setMultiAgentResult: (result: MultiAgentResult) => void;
  clearAll: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  jd: null,
  resume: null,
  screeningResult: null,
  questions: null,
  evaluation: null,
  risks: null,
  multiAgentResult: null,

  setJD: (jd) => set({ jd }),
  setResume: (resume) => set({ resume }),
  setScreeningResult: (screeningResult) => set({ screeningResult }),
  setQuestions: (questions) => set({ questions }),
  setEvaluation: (evaluation) => set({ evaluation }),
  setRisks: (risks) => set({ risks }),
  setMultiAgentResult: (multiAgentResult) => set({ multiAgentResult }),
  clearAll: () => set({
    jd: null,
    resume: null,
    screeningResult: null,
    questions: null,
    evaluation: null,
    risks: null,
    multiAgentResult: null,
  }),
}));
