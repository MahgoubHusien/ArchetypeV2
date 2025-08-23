// Common constants and types used throughout the application

export const PERSONA_COLORS = [
  'bg-pink-100 text-pink-700 border-pink-300',
  'bg-blue-100 text-blue-700 border-blue-300',
  'bg-green-100 text-green-700 border-green-300',
  'bg-purple-100 text-purple-700 border-purple-300',
  'bg-orange-100 text-orange-700 border-orange-300',
  'bg-indigo-100 text-indigo-700 border-indigo-300',
  'bg-yellow-100 text-yellow-700 border-yellow-300',
  'bg-teal-100 text-teal-700 border-teal-300',
];

export const PRESET_PERSONAS = [
  { 
    id: '1', 
    name: 'Tech-Savvy Millennial', 
    age: '28', 
    context: 'Frequent online shopper, uses mobile primarily', 
    color: PERSONA_COLORS[0] 
  },
  { 
    id: '2', 
    name: 'Senior User', 
    age: '65', 
    context: 'Less familiar with technology, needs clear instructions', 
    color: PERSONA_COLORS[1] 
  },
  { 
    id: '3', 
    name: 'Busy Parent', 
    age: '35', 
    context: 'Time-constrained, shopping for family needs', 
    color: PERSONA_COLORS[2] 
  },
  { 
    id: '4', 
    name: 'Budget Conscious Student', 
    age: '22', 
    context: 'Price-sensitive, looks for deals and discounts', 
    color: PERSONA_COLORS[3] 
  },
  { 
    id: '5', 
    name: 'Power User', 
    age: '30', 
    context: 'Tech expert, expects advanced features and shortcuts', 
    color: PERSONA_COLORS[4] 
  },
];

// Agent and interaction status types
export type AgentStatus = 'pending' | 'running' | 'completed' | 'failed';
export type TestViewType = 'dashboard' | 'test-results';
export type InsightType = 'issue' | 'success' | 'improvement' | 'observation';
export type SeverityLevel = 'low' | 'medium' | 'high';

// Common interfaces
export interface PersonaConfig {
  id: string;
  name: string;
  age: string;
  context: string;
  color: string;
}

export interface TestConfig {
  question: string;
  url: string;
  selector: string;
  personas: PersonaConfig[];
  runId?: string;
}

export interface UXTest {
  id: string;
  title: string;
  question: string;
  date: string;
  time: string;
  personas: { name: string; color: string }[];
  status: AgentStatus;
  url?: string;
}

// Action type mappings
export const ACTION_TYPE_CONFIG = {
  click: {
    icon: 'MousePointer',
    color: 'bg-blue-50 text-blue-700 border-blue-200',
    label: 'Click'
  },
  type: {
    icon: 'Type',
    color: 'bg-green-50 text-green-700 border-green-200',
    label: 'Type'
  },
  scroll: {
    icon: 'Eye',
    color: 'bg-purple-50 text-purple-700 border-purple-200',
    label: 'Scroll'
  },
  wait: {
    icon: 'Clock',
    color: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    label: 'Wait'
  },
  default: {
    icon: 'MousePointer',
    color: 'bg-gray-50 text-gray-700 border-gray-200',
    label: 'Action'
  }
} as const;

// Status configurations
export const STATUS_CONFIG = {
  pending: {
    color: 'bg-gray-100 text-gray-700',
    icon: 'Clock',
    label: 'Pending'
  },
  running: {
    color: 'bg-blue-100 text-blue-700',
    icon: 'Loader',
    label: 'Running'
  },
  completed: {
    color: 'bg-green-100 text-green-700',
    icon: 'CheckCircle2',
    label: 'Completed'
  },
  failed: {
    color: 'bg-red-100 text-red-700',
    icon: 'AlertCircle',
    label: 'Failed'
  }
} as const;

// Insight type configurations
export const INSIGHT_TYPE_CONFIG = {
  issue: {
    icon: 'AlertTriangle',
    color: 'text-red-600',
    label: 'Issue'
  },
  success: {
    icon: 'CheckCircle2',
    color: 'text-green-600',
    label: 'Success'
  },
  improvement: {
    icon: 'TrendingUp',
    color: 'text-blue-600',
    label: 'Improvement'
  },
  observation: {
    icon: 'Eye',
    color: 'text-purple-600',
    label: 'Observation'
  }
} as const;

// Severity configurations
export const SEVERITY_CONFIG = {
  high: 'bg-red-100 text-red-800 border-red-200',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  low: 'bg-green-100 text-green-800 border-green-200'
} as const;

// Common polling intervals
export const POLLING_INTERVALS = {
  AGENT_STATUS: 2000, // 2 seconds
  DATA_REFRESH: 5000,  // 5 seconds
} as const;

// Animation configurations
export const ANIMATIONS = {
  PAGE_TRANSITION: {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 }
  },
  FADE_IN: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 }
  }
} as const;