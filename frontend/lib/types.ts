/** Mirrors of the backend Pydantic contracts (backend/app/schemas.py). */

export interface StudentProfileIn {
  name: string;
  age?: number | null;
  interests: string[];
  prior_knowledge: "none" | "some" | "comfortable";
  preferred_theme?: string | null;
  learning_goal?: string | null;
  difficulty_preference: "gentle" | "standard" | "challenging";
}

export interface MentorCharacter {
  name: string;
  role: string;
  personality: string;
}

export interface MissionArcEntry {
  mission_id: string;
  python_concept: string;
  story_purpose: string;
  learning_objective: string;
  difficulty: number;
}

export interface StoryArc {
  student_profile_summary: string;
  course_topic: string;
  theme: string;
  story_title: string;
  protagonist_role: string;
  world_description: string;
  central_conflict: string;
  main_goal: string;
  mentor_character: MentorCharacter;
  mission_arc: MissionArcEntry[];
  final_challenge: { description: string; concepts_combined: string[] };
}

export interface HiddenTest {
  assertion: string;
  description: string;
}

export interface Mission {
  mission_id: string;
  module: string;
  difficulty: number;
  theme: string;
  title: string;
  story_context: {
    previous_state: string;
    current_problem: string;
    why_this_matters: string;
    narrative_stakes: string;
  };
  learning_objective: string;
  concept_explanation: string;
  starter_code: string;
  student_task: string;
  expected_solution_description: string;
  hidden_tests: HiddenTest[];
  hints: string[];
  success_feedback: { technical_feedback: string; story_feedback: string };
  failure_feedback: { technical_feedback: string; story_feedback: string };
  remediation: { simpler_explanation: string; smaller_subtask: string };
  next_mission_rules: { on_success: string; on_failure: string };
}

export interface Adventure {
  id: number;
  student_id: number;
  generator: "llm" | "template";
  format: string;
  story_arc: StoryArc;
  missions: Mission[];
}

export interface MissionProgress {
  mission_id: string;
  status: "locked" | "available" | "completed";
  attempts: number;
}

export interface Progress {
  adventure_id: number;
  missions: MissionProgress[];
  completed_count: number;
  total_count: number;
}

export interface TestResult {
  description: string;
  passed: boolean;
  error: string | null;
}

export interface RunResult {
  output: string;
  error: string | null;
  passed: boolean;
  results: TestResult[];
}

export interface SubmissionResult {
  recorded: boolean;
  passed: boolean;
  attempts: number;
  next_action: "next" | "finish" | "retry" | "remediate";
  hint_level: number;
  hint: string | null;
  technical_feedback: string;
  story_feedback: string;
  remediation: { simpler_explanation: string; smaller_subtask: string } | null;
}
