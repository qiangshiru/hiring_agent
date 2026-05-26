export interface JDParseResult {
  工作经验?: {
    min_years?: number;
    max_years?: number;
  };
  学历?: {
    必须?: string[];
    加分?: string[];
  };
  技术栈?: {
    必须?: string[];
    加分?: string[];
  };
  [key: string]: unknown;
}

export interface ResumeParseResult {
  姓名?: string;
  教育?: Array<{
    学校?: string;
    学历?: string;
    专业?: string;
  }>;
  工作经验?: Array<{
    公司?: string;
    职位?: string;
    技能?: string[];
  }>;
  项目?: Array<{
    项目名称?: string;
    描述?: string;
    技术栈?: string[];
  }>;
  技能?: string[];
  [key: string]: unknown;
}

export interface ScreeningResult {
  技术匹配度: number;
  AI能力深度: number;
  工程能力: number;
  教育背景: number;
  稳定性: number;
  综合评分: number;
  筛选结果: string;
  理由: string[];
}

export interface Question {
  id: string;
  type: string;
  content: string;
  difficulty: string;
  scoring_points?: string[];
  follow_up_hints?: string[];
}

export interface QuestionGenerationResult {
  questions: Question[];
  difficulty_distribution: Record<string, number>;
}

export interface EvaluationResult {
  技术深度: {
    dimension: string;
    level: string;
    score: number;
  };
  沟通表达: {
    dimension: string;
    level: string;
    score: number;
  };
  真实性: {
    dimension: string;
    level: string;
    score: number;
  };
  系统设计: {
    dimension: string;
    level: string;
    score: number;
  };
  工程能力: {
    dimension: string;
    level: string;
    score: number;
  };
  综合评分: number;
  优势: string[];
  不足: string[];
}

export interface RiskItem {
  risk_type: string;
  risk_level: string;
  description: string;
  confidence: number;
}

export interface RiskDetectionResult {
  risks: RiskItem[];
  overall_risk_level: string;
  risk_summary: string;
}

export interface MultiAgentResult {
  hr_agent_output: Record<string, unknown> | null;
  tech_agent_output: Record<string, unknown> | null;
  architect_agent_output: Record<string, unknown> | null;
  risk_agent_output: Record<string, unknown> | null;
  final_recommendation: string;
  agent_recommendations: Record<string, string>;
  errors?: string[];
}
