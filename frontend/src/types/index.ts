export interface EducationRequirement {
  必须?: string[];
  加分?: string[];
}

export interface WorkExperienceRequirement {
  min_years?: number;
  max_years?: number;
}

export interface TechStackRequirement {
  must: string[];
  bonus: string[];
}

export interface JDParseResult {
  学历: EducationRequirement;
  工作经验: WorkExperienceRequirement;
  技术栈: TechStackRequirement;
  行业经验: string[];
  城市要求: string[];
  薪资范围?: {
    min_monthly?: number;
    max_monthly?: number;
    currency?: string;
    raw?: string;
  } | null;
}

export interface Education {
  [key: string]: unknown;
  学校?: string;
  学历?: string;
  专业?: string;
  开始时间?: string;
  结束时间?: string;
  描述?: string;
  置信度?: number;
}

export interface WorkExperience {
  [key: string]: unknown;
  公司?: string;
  职位?: string;
  开始时间?: string;
  结束时间?: string;
  描述?: string;
  技能?: string[];
  置信度?: number;
}

export interface Project {
  [key: string]: unknown;
  项目名称?: string;
  角色?: string;
  开始时间?: string;
  结束时间?: string;
  描述?: string;
  技术栈?: string[];
  置信度?: number;
}

export interface SkillItem {
  名称: string;
  类别?: string;
  熟练度?: string;
  置信度?: number;
}

export interface ResumeParseResult {
  姓名?: string | null;
  性别?: string | null;
  年龄?: number | null;
  电话?: string | null;
  邮箱?: string | null;
  城市?: string | null;
  教育?: Education[];
  工作经验?: WorkExperience[];
  项目?: Project[];
  技能?: SkillItem[];
  自我评价?: string | null;
  原始文本?: string | null;
  解析耗时_ms?: number;
  [key: string]: unknown;
}

// Scoring types (matches backend /scoring endpoints)
export interface DimensionScore {
  name: string;
  score: number;
  weight: number;
  confidence: number;
  reason?: string;
  details?: Record<string, unknown> | null;
}

export interface ScoringResult {
  total: number;
  dimensions: DimensionScore[];
  overall_confidence: number;
  summary?: string;
  recommendation?: string;
}

export interface DimensionWeights {
  tech_match: number;
  ai_depth: number;
  engineering: number;
  education: number;
  stability: number;
}

// Screening types (matches backend /screening endpoints)
export interface ScreeningResult {
  passed: boolean;
  reasons: string[];
  failed_rules: string[];
  matched_rules: string[];
  confidence: number;
}

export interface Question {
  id: string;
  type: string;
  difficulty: string;
  content: string;
  expected_skills?: string[];
  scoring_guide?: string[];
  follow_up_hints?: string[];
  time_minutes?: number;
  tags?: string[];
}

export interface QuestionGenerationConfig {
  total_questions: number;
  difficulty_distribution: Record<string, number>;
  type_distribution: Record<string, number>;
}

export interface QuestionGenerationResult {
  questions: Question[];
  config: QuestionGenerationConfig;
  difficulty_distribution: Record<string, number>;
  type_distribution: Record<string, number>;
}

export interface DimensionEvaluation {
  dimension: string;
  level: string;
  score: number;
  evidence?: unknown[];
  comment?: string;
}

export interface EvaluationResult {
  技术深度: DimensionEvaluation;
  沟通表达: DimensionEvaluation;
  真实性: DimensionEvaluation;
  系统设计: DimensionEvaluation;
  工程能力: DimensionEvaluation;
  综合评分: number;
  优势: string[];
  不足: string[];
}

export interface RiskItem {
  risk_type: string;
  risk_level: string;
  description: string;
  evidence?: unknown[];
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
