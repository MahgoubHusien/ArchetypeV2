'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { agentApi, Agent } from '@/lib/api';
import { AgentStatus, POLLING_INTERVALS } from '@/lib/constants';
import { calculateProgress } from '@/lib/formatters';

interface AgentWithProgress extends Agent {
  progress: number;
}

interface UseAgentPollingReturn {
  agents: AgentWithProgress[];
  overallProgress: number;
  isPolling: boolean;
  error: string | null;
  startPolling: (runId: string) => void;
  stopPolling: () => void;
  retryPolling: () => void;
}

export function useAgentPolling(): UseAgentPollingReturn {
  const [agents, setAgents] = useState<AgentWithProgress[]>([]);
  const [overallProgress, setOverallProgress] = useState(0);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollingRef = useRef<NodeJS.Timeout>();
  const currentRunIdRef = useRef<string | null>(null);

  const getAgentProgress = useCallback((status: AgentStatus): number => {
    switch (status) {
      case 'pending': return 0;
      case 'running': return 50;
      case 'completed': return 100;
      case 'failed': return 100;
      default: return 0;
    }
  }, []);

  const pollAgentStatus = useCallback(async () => {
    const runId = currentRunIdRef.current;
    if (!runId) return;

    try {
      const response = await agentApi.getByRunId(runId);
      const agentData: Agent[] = response.data;

      const agentsWithProgress: AgentWithProgress[] = agentData.map((agent, index) => ({
        ...agent,
        progress: getAgentProgress(agent.status as AgentStatus)
      }));

      setAgents(agentsWithProgress);

      // Calculate overall progress
      const completedCount = agentsWithProgress.filter(a => a.status === 'completed').length;
      const runningCount = agentsWithProgress.filter(a => a.status === 'running').length;
      const totalCount = agentsWithProgress.length;

      const progress = calculateProgress(completedCount, runningCount, totalCount);
      setOverallProgress(progress);

      // Check if all agents are done
      const allDone = agentsWithProgress.every(a => 
        a.status === 'completed' || a.status === 'failed'
      );

      if (allDone) {
        setIsPolling(false);
        return true; // Indicate completion
      }

      return false;
    } catch (err) {
      console.error('Error polling agent status:', err);
      setError('Failed to get agent status');
      setIsPolling(false);
      return false;
    }
  }, [getAgentProgress]);

  const startPolling = useCallback((runId: string) => {
    currentRunIdRef.current = runId;
    setIsPolling(true);
    setError(null);

    const poll = async () => {
      const isComplete = await pollAgentStatus();
      
      if (!isComplete && isPolling) {
        pollingRef.current = setTimeout(poll, POLLING_INTERVALS.AGENT_STATUS);
      }
    };

    poll();
  }, [pollAgentStatus, isPolling]);

  const stopPolling = useCallback(() => {
    setIsPolling(false);
    currentRunIdRef.current = null;
    if (pollingRef.current) {
      clearTimeout(pollingRef.current);
      pollingRef.current = undefined;
    }
  }, []);

  const retryPolling = useCallback(() => {
    if (currentRunIdRef.current) {
      setError(null);
      startPolling(currentRunIdRef.current);
    }
  }, [startPolling]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearTimeout(pollingRef.current);
      }
    };
  }, []);

  return {
    agents,
    overallProgress,
    isPolling,
    error,
    startPolling,
    stopPolling,
    retryPolling
  };
}