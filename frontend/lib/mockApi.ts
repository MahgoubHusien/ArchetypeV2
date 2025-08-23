// Mock API implementation for development
import { Agent, Interaction, Run, CreateRunRequest, CreateRunResponse } from './api';

// Mock data
const mockRuns: Run[] = [
  {
    run_id: '550e8400-e29b-41d4-a716-446655440001',
    state: 'completed',
    url: 'https://example.com',
    ux_question: 'How easy is it to find the signup button?',
    created_at: new Date().toISOString(),
  },
  {
    run_id: '550e8400-e29b-41d4-a716-446655440002',
    state: 'running',
    url: 'https://myapp.com',
    ux_question: 'Can users easily navigate to the pricing page?',
    created_at: new Date(Date.now() - 86400000).toISOString(), // Yesterday
  },
];

const mockAgents: Agent[] = [
  {
    agent_id: '650e8400-e29b-41d4-a716-446655440001',
    run_id: '550e8400-e29b-41d4-a716-446655440001',
    persona: 'Tech Savvy User',
    status: 'completed',
    started_at: new Date().toISOString(),
    ended_at: new Date().toISOString(),
  },
  {
    agent_id: '650e8400-e29b-41d4-a716-446655440002',
    run_id: '550e8400-e29b-41d4-a716-446655440001',
    persona: 'First-time User',
    status: 'completed',
    started_at: new Date().toISOString(),
    ended_at: new Date().toISOString(),
  },
  {
    agent_id: '650e8400-e29b-41d4-a716-446655440003',
    run_id: '550e8400-e29b-41d4-a716-446655440002',
    persona: 'Mobile User',
    status: 'running',
    started_at: new Date().toISOString(),
    ended_at: new Date().toISOString(),
  },
  {
    agent_id: '650e8400-e29b-41d4-a716-446655440004',
    run_id: '550e8400-e29b-41d4-a716-446655440002',
    persona: 'Power User',
    status: 'running',
    started_at: new Date().toISOString(),
    ended_at: new Date().toISOString(),
  },
];

const mockInteractions: Interaction[] = [
  {
    interaction_id: '750e8400-e29b-41d4-a716-446655440001',
    agent_id: '650e8400-e29b-41d4-a716-446655440001',
    step: 1,
    intent: 'Find signup button',
    action_type: 'click',
    selector: 'button.signup',
    result: 'Successfully found and clicked signup button',
    created_at: new Date().toISOString(),
  },
];

// Mock API implementation
export const mockRunApi = {
  getAll: () => Promise.resolve({ data: mockRuns }),
  getById: (runId: string) => {
    const run = mockRuns.find(r => r.run_id === runId);
    return run ? Promise.resolve({ data: run }) : Promise.reject(new Error('Run not found'));
  },
  create: (data: CreateRunRequest): Promise<{ data: CreateRunResponse }> => {
    const newRun: Run = {
      run_id: `550e8400-e29b-41d4-a716-${Date.now()}`,
      state: 'running',
      url: data.url,
      ux_question: data.ux_question,
      created_at: new Date().toISOString(),
    };
    mockRuns.push(newRun);
    
    // Create mock agents for each persona
    data.personas.forEach((persona, index) => {
      mockAgents.push({
        agent_id: `650e8400-e29b-41d4-a716-${Date.now()}-${index}`,
        run_id: newRun.run_id,
        persona: persona.name,
        status: 'running',
        started_at: new Date().toISOString(),
        ended_at: new Date().toISOString(),
      });
    });
    
    return Promise.resolve({
      data: {
        run_id: newRun.run_id,
        message: 'Test created successfully',
      },
    });
  },
};

export const mockAgentApi = {
  getAll: () => Promise.resolve({ data: mockAgents }),
  getById: (agentId: string) => {
    const agent = mockAgents.find(a => a.agent_id === agentId);
    return agent ? Promise.resolve({ data: agent }) : Promise.reject(new Error('Agent not found'));
  },
  getByRunId: (runId: string) => {
    const agents = mockAgents.filter(a => a.run_id === runId);
    return Promise.resolve({ data: agents });
  },
};

export const mockInteractionApi = {
  getAll: () => Promise.resolve({ data: mockInteractions }),
  getById: (interactionId: string) => {
    const interaction = mockInteractions.find(i => i.interaction_id === interactionId);
    return interaction ? Promise.resolve({ data: interaction }) : Promise.reject(new Error('Interaction not found'));
  },
  getByAgentId: (agentId: string) => {
    const interactions = mockInteractions.filter(i => i.agent_id === agentId);
    return Promise.resolve({ data: interactions });
  },
};