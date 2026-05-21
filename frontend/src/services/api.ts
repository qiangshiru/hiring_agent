import axios from 'axios';
import {
  JDParseResult,
  ResumeParseResult,
  ScreeningResult,
  QuestionGenerationResult,
  EvaluationResult,
  RiskDetectionResult,
  MultiAgentResult,
} from '@/types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const jdApi = {
  parse: async (text: string): Promise<JDParseResult> => {
    const response = await api.post('/jd/parse', { text });
    return response.data;
  },
};

export const resumeApi = {
  parse: async (text: string): Promise<ResumeParseResult> => {
    const response = await api.post('/resume/parse', { text });
    return response.data;
  },
};

export const screeningApi = {
  screen: async (jd: JDParseResult, resume: ResumeParseResult): Promise<ScreeningResult> => {
    const response = await api.post('/screening/screen', { jd, resume });
    return response.data;
  },
};

export const questionsApi = {
  generate: async (jd: JDParseResult, resume: ResumeParseResult): Promise<QuestionGenerationResult> => {
    const response = await api.post('/questions/generate', { jd, resume });
    return response.data;
  },
};

export const evaluationApi = {
  evaluate: async (interviewRecord: unknown): Promise<EvaluationResult> => {
    const response = await api.post('/evaluation/evaluate', interviewRecord);
    return response.data;
  },
  detectRisks: async (interviewRecord: unknown, resume?: ResumeParseResult): Promise<RiskDetectionResult> => {
    const response = await api.post('/evaluation/detect-risks', { interviewRecord, resume });
    return response.data;
  },
};

export const multiAgentApi = {
  evaluate: async (jd: JDParseResult, resume: ResumeParseResult): Promise<MultiAgentResult> => {
    const response = await api.post('/multi-agent/evaluate', { jd, resume });
    return response.data;
  },
};
