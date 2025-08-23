// Enhanced TypeScript interfaces for better type safety

import { Agent, Interaction, Run } from '@/lib/api';
import { 
  AgentStatus, 
  InsightType, 
  SeverityLevel, 
  PersonaConfig 
} from '@/lib/constants';

// Enhanced component prop types
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface LoadingStateProps {
  loading: boolean;
  error?: string | null;
  onRetry?: () => void;
}

// Test configuration interfaces
export interface EnhancedTestConfig {
  question: string;
  url: string;
  selector?: string;
  personas: PersonaConfig[];
  runId?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface TestFormData {
  url: string;
  question: string;
  selector: string;
  personas: PersonaConfig[];
}

export interface TestValidationErrors {
  url?: string;
  question?: string;
  personas?: string;
  [key: string]: string | undefined;
}

// Dashboard interfaces
export interface DashboardProps extends BaseComponentProps {
  onNewTest: () => void;
  onSelectTest: (test: UXTest) => void;
}

export interface UXTest {
  id: string;
  title: string;
  question: string;
  date: string;
  time: string;
  personas: Array<{
    name: string;
    color: string;
  }>;
  status: AgentStatus;
  url?: string;
  completionRate?: number;
  averageSteps?: number;
  duration?: number;
}

// Agent and interaction interfaces
export interface AgentWithProgress extends Agent {
  progress: number;
  persona: string;
  color: string;
}

export interface InteractionWithContext extends Interaction {
  agent?: Agent;
  persona: string;
  color: string;
  formattedTime?: string;
}

export interface InteractionFilters {
  selectedAgent: string;
  searchTerm: string;
  actionFilter: string;
}

// UX Analysis interfaces
export interface UXInsight {
  id: string;
  type: InsightType;
  severity: SeverityLevel;
  title: string;
  description: string;
  persona: string;
  personaColor: string;
  step: number;
  interactions: Interaction[];
  recommendation?: string;
  impact?: string;
  evidence?: string;
  createdAt: string;
}

export interface AnalysisMetrics {
  totalInteractions: number;
  averageSteps: number;
  completionRate: number;
  averageTime: number;
  successRate: number;
  failurePoints: string[];
  successPatterns: string[];
  mostCommonActions: Array<{
    action: string;
    count: number;
    percentage: number;
  }>;
}

export interface UXReportProps extends BaseComponentProps {
  testConfig: EnhancedTestConfig | null;
  onGenerateTicket: (insight: UXInsight) => void;
  onJumpToTranscript: (moment: string) => void;
}

// Wizard and form interfaces
export interface TestSetupWizardProps extends BaseComponentProps {
  isOpen: boolean;
  onClose: () => void;
  onRunTest: (config: EnhancedTestConfig) => Promise<void>;
}

export interface WizardStepProps extends BaseComponentProps {
  data: TestFormData;
  errors: TestValidationErrors;
  onChange: (data: Partial<TestFormData>) => void;
  onError: (errors: Partial<TestValidationErrors>) => void;
}

// Progress tracking interfaces
export interface SwarmProgressProps extends BaseComponentProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
  testConfig: EnhancedTestConfig | null;
}

export interface ProgressState {
  agents: AgentWithProgress[];
  overallProgress: number;
  startTime: Date | null;
  elapsedTime: number;
  isPolling: boolean;
  error: string | null;
}

// Transcript interfaces
export interface TranscriptViewProps extends BaseComponentProps {
  testConfig: EnhancedTestConfig | null;
  onSelectInsight: (interaction: InteractionWithContext) => void;
}

export interface TranscriptState {
  interactions: InteractionWithContext[];
  agents: Agent[];
  filters: InteractionFilters;
  loading: boolean;
  error: string | null;
}

// Modal interfaces
export interface TicketModalProps extends BaseComponentProps {
  isOpen: boolean;
  onClose: () => void;
  insight: UXInsight | null;
}

export interface TicketData {
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  assignee?: string;
  labels: string[];
  dueDate?: string;
}

// Hook return types
export interface UseAgentPollingReturn {
  agents: AgentWithProgress[];
  overallProgress: number;
  isPolling: boolean;
  error: string | null;
  startPolling: (runId: string) => void;
  stopPolling: () => void;
  retryPolling: () => void;
}

export interface UseTestDataReturn {
  tests: UXTest[];
  loading: boolean;
  error: string | null;
  loadTests: () => Promise<void>;
  retryLoad: () => void;
  refreshTests: () => void;
}

export interface UseInteractionsReturn {
  interactions: InteractionWithContext[];
  agents: Agent[];
  loading: boolean;
  error: string | null;
  loadInteractions: (runId: string) => Promise<void>;
  filteredInteractions: InteractionWithContext[];
  setFilters: (filters: Partial<InteractionFilters>) => void;
  clearFilters: () => void;
  uniqueActionTypes: string[];
}

// API enhancement interfaces
export interface APIResponse<T> {
  data: T;
  status: number;
  message?: string;
  timestamp: string;
}

export interface APIError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

// Configuration interfaces
export interface AppConfig {
  apiUrl: string;
  pollingInterval: number;
  maxRetries: number;
  timeout: number;
  enableAnalytics: boolean;
  debugMode: boolean;
}

// Event interfaces
export interface TestEvent {
  type: 'test_started' | 'test_completed' | 'test_failed' | 'agent_update';
  payload: Record<string, any>;
  timestamp: string;
}

export interface UserAction {
  type: string;
  target?: string;
  data?: Record<string, any>;
  timestamp: string;
}