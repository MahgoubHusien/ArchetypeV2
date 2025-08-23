import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Agent {
  agent_id: string;
  run_id: string;
  persona: string;
  status: string;
  started_at: string;
  ended_at: string;
}

export interface Interaction {
  interaction_id: string;
  agent_id: string;
  step: number;
  intent?: string;
  action_type?: string;
  selector?: string;
  result: string;
  created_at: string;
}

export interface Run {
  run_id: string;
  state: string;
  url: string;
  ux_question?: string;
  created_at: string;
}

export const agentApi = {
  getAll: () => api.get<Agent[]>('/agents'),
  getById: (agentId: string) => api.get<Agent>(`/agents/${agentId}`),
  getByRunId: (runId: string) => api.get<Agent[]>(`/agents/by-run/${runId}`),
};

export const interactionApi = {
  getAll: () => api.get<Interaction[]>('/interactions'),
  getById: (interactionId: string) => api.get<Interaction>(`/interactions/${interactionId}`),
  getByAgentId: (agentId: string) => api.get<Interaction[]>(`/interactions/by-agent/${agentId}`),
};

export const runApi = {
  getAll: () => api.get<Run[]>('/runs'),
  getById: (runId: string) => api.get<Run>(`/runs/${runId}`),
};

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      console.error('Network Error:', error.request);
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;