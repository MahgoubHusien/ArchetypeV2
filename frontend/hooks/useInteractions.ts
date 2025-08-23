'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { agentApi, interactionApi, Agent, Interaction } from '@/lib/api';
import { PERSONA_COLORS } from '@/lib/constants';
import { getPersonaColor } from '@/lib/formatters';

export interface InteractionWithAgent extends Interaction {
  agent?: Agent;
  persona?: string;
  color?: string;
}

interface UseInteractionsReturn {
  interactions: InteractionWithAgent[];
  agents: Agent[];
  loading: boolean;
  error: string | null;
  loadInteractions: (runId: string) => Promise<void>;
  filteredInteractions: InteractionWithAgent[];
  setFilters: (filters: {
    selectedAgent?: string;
    searchTerm?: string;
    actionFilter?: string;
  }) => void;
  clearFilters: () => void;
}

interface Filters {
  selectedAgent: string;
  searchTerm: string;
  actionFilter: string;
}

export function useInteractions(): UseInteractionsReturn {
  const [interactions, setInteractions] = useState<InteractionWithAgent[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFiltersState] = useState<Filters>({
    selectedAgent: 'all',
    searchTerm: '',
    actionFilter: 'all'
  });

  const loadInteractions = useCallback(async (runId: string) => {
    setLoading(true);
    setError(null);

    try {
      // Load agents for this run
      const agentsResponse = await agentApi.getByRunId(runId);
      const agentData = agentsResponse.data;
      setAgents(agentData);

      // Load interactions for each agent
      const interactionPromises = agentData.map(agent => 
        interactionApi.getByAgentId(agent.agent_id)
      );
      
      const interactionResponses = await Promise.all(interactionPromises);
      
      // Combine all interactions and sort by created_at
      const allInteractions: InteractionWithAgent[] = [];
      
      interactionResponses.forEach((response, agentIndex) => {
        const agent = agentData[agentIndex];
        const agentInteractions = response.data.map((interaction: Interaction) => ({
          ...interaction,
          agent,
          persona: agent.persona || `Agent ${agentIndex + 1}`,
          color: getPersonaColor(agentIndex, PERSONA_COLORS)
        }));
        allInteractions.push(...agentInteractions);
      });

      // Sort by step and created_at
      allInteractions.sort((a, b) => {
        if (a.step !== b.step) {
          return a.step - b.step;
        }
        return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      });

      setInteractions(allInteractions);
    } catch (err) {
      console.error('Error loading interactions:', err);
      setError('Failed to load test interactions');
    } finally {
      setLoading(false);
    }
  }, []);

  const filteredInteractions = useMemo(() => {
    return interactions.filter(interaction => {
      // Agent filter
      if (filters.selectedAgent !== 'all' && interaction.agent_id !== filters.selectedAgent) {
        return false;
      }

      // Action type filter
      if (filters.actionFilter !== 'all' && interaction.action_type !== filters.actionFilter) {
        return false;
      }

      // Search filter
      if (filters.searchTerm) {
        const searchLower = filters.searchTerm.toLowerCase();
        return (
          interaction.intent?.toLowerCase().includes(searchLower) ||
          interaction.result?.toLowerCase().includes(searchLower) ||
          interaction.selector?.toLowerCase().includes(searchLower) ||
          interaction.persona?.toLowerCase().includes(searchLower)
        );
      }

      return true;
    });
  }, [interactions, filters]);

  const setFilters = useCallback((newFilters: Partial<Filters>) => {
    setFiltersState(prev => ({ ...prev, ...newFilters }));
  }, []);

  const clearFilters = useCallback(() => {
    setFiltersState({
      selectedAgent: 'all',
      searchTerm: '',
      actionFilter: 'all'
    });
  }, []);

  return {
    interactions,
    agents,
    loading,
    error,
    loadInteractions,
    filteredInteractions,
    setFilters,
    clearFilters
  };
}