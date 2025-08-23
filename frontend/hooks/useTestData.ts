'use client';

import { useState, useEffect, useCallback } from 'react';
import { runApi, agentApi, interactionApi, Run, Agent, Interaction } from '@/lib/api';
import { UXTest } from '@/lib/constants';
import { formatDate, formatTime, getPersonaColor } from '@/lib/formatters';
import { PERSONA_COLORS } from '@/lib/constants';

interface UseTestDataReturn {
  tests: UXTest[];
  loading: boolean;
  error: string | null;
  loadTests: () => Promise<void>;
  retryLoad: () => void;
}

export function useTestData(): UseTestDataReturn {
  const [tests, setTests] = useState<UXTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadTests = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const runsResponse = await runApi.getAll();
      const runs = runsResponse.data;
      
      if (!runs || runs.length === 0) {
        setTests([]);
        return;
      }

      const testList: UXTest[] = [];
      const agentPromises = runs.map(run => agentApi.getByRunId(run.run_id));
      
      const agentResponses = await Promise.all(agentPromises);
      
      runs.forEach((run, index) => {
        const agents = agentResponses[index].data;
        
        const date = new Date(run.created_at);
        const formattedDate = formatDate(date);
        const formattedTime = formatTime(date);
        
        const personas = agents.map((agent, idx) => ({
          name: agent.persona || `Agent ${idx + 1}`,
          color: getPersonaColor(idx, PERSONA_COLORS)
        }));
        
        const allCompleted = agents.every(a => a.status === 'completed');
        const anyFailed = agents.some(a => a.status === 'failed');
        
        testList.push({
          id: run.run_id,
          title: run.ux_question ? `${run.url} Analysis` : 'UX Test',
          question: run.ux_question || 'No question provided',
          date: formattedDate,
          time: formattedTime,
          personas,
          status: anyFailed ? 'failed' : (allCompleted ? 'completed' : 'running'),
          url: run.url
        });
      });
      
      setTests(testList);
    } catch (err: any) {
      console.error('Error loading tests:', err);
      
      if (err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
        setError('Backend server is not running. Please start the server on port 8000.');
      } else {
        setError('Failed to load tests');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const retryLoad = useCallback(() => {
    loadTests();
  }, [loadTests]);

  useEffect(() => {
    loadTests();
  }, [loadTests]);

  return {
    tests,
    loading,
    error,
    loadTests,
    retryLoad
  };
}