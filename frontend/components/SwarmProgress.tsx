'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Progress } from './ui/progress';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent } from './ui/card';
import { CheckCircle2, Clock, User, AlertCircle, X } from 'lucide-react';
import { agentApi, Agent } from '@/lib/api';

interface SwarmProgressProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
  testConfig: any;
}

interface AgentStatus {
  agent_id: string;
  persona: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  started_at?: string;
  ended_at?: string;
  progress?: number;
}

export function SwarmProgress({ isOpen, onClose, onComplete, testConfig }: SwarmProgressProps) {
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [overallProgress, setOverallProgress] = useState(0);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    if (isOpen && testConfig?.runId) {
      setStartTime(new Date());
      setIsPolling(true);
      setError(null);
      pollAgentStatus();
    } else {
      setIsPolling(false);
    }

    return () => {
      setIsPolling(false);
    };
  }, [isOpen, testConfig?.runId]);

  // Timer for elapsed time
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (startTime && isPolling) {
      interval = setInterval(() => {
        setElapsedTime(Date.now() - startTime.getTime());
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [startTime, isPolling]);

  const pollAgentStatus = async () => {
    if (!testConfig?.runId) return;

    try {
      const response = await agentApi.getByRunId(testConfig.runId);
      const agentData: Agent[] = response.data;

      const agentStatuses: AgentStatus[] = agentData.map((agent, index) => ({
        agent_id: agent.agent_id,
        persona: agent.persona || `Agent ${index + 1}`,
        status: agent.status as 'pending' | 'running' | 'completed' | 'failed',
        started_at: agent.started_at,
        ended_at: agent.ended_at,
        progress: getAgentProgress(agent.status)
      }));

      setAgents(agentStatuses);

      // Calculate overall progress
      const totalAgents = agentStatuses.length;
      const completedAgents = agentStatuses.filter(a => a.status === 'completed').length;
      const runningAgents = agentStatuses.filter(a => a.status === 'running').length;
      
      const progress = totalAgents > 0 
        ? ((completedAgents + (runningAgents * 0.5)) / totalAgents) * 100
        : 0;
      
      setOverallProgress(Math.min(progress, 100));

      // Check if all agents are done
      const allDone = agentStatuses.every(a => 
        a.status === 'completed' || a.status === 'failed'
      );

      if (allDone) {
        setIsPolling(false);
        // Wait a moment to show completion, then call onComplete
        setTimeout(() => {
          onComplete();
        }, 2000);
      } else if (isPolling) {
        // Continue polling every 2 seconds
        setTimeout(pollAgentStatus, 2000);
      }

    } catch (err) {
      console.error('Error polling agent status:', err);
      setError('Failed to get agent status');
      setIsPolling(false);
    }
  };

  const getAgentProgress = (status: string): number => {
    switch (status) {
      case 'pending': return 0;
      case 'running': return 50;
      case 'completed': return 100;
      case 'failed': return 100; // Progress complete but failed
      default: return 0;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-gray-100 text-gray-700';
      case 'running': return 'bg-blue-100 text-blue-700';
      case 'completed': return 'bg-green-100 text-green-700';
      case 'failed': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock className="w-4 h-4" />;
      case 'running': return <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />;
      case 'completed': return <CheckCircle2 className="w-4 h-4" />;
      case 'failed': return <AlertCircle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const formatElapsedTime = (ms: number): string => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const completedCount = agents.filter(a => a.status === 'completed').length;
  const failedCount = agents.filter(a => a.status === 'failed').length;
  const runningCount = agents.filter(a => a.status === 'running').length;

  const handleCancel = () => {
    setIsPolling(false);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Running UX Test</span>
            <Button variant="ghost" size="sm" onClick={handleCancel}>
              <X className="w-4 h-4" />
            </Button>
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6 py-4">
          {/* Overall Progress */}
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">Overall Progress</span>
              <span className="text-gray-500">
                {startTime && `${formatElapsedTime(elapsedTime)} elapsed`}
              </span>
            </div>
            <Progress value={overallProgress} className="h-3" />
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>
                {completedCount} of {agents.length} agents completed
              </span>
              <span>{Math.round(overallProgress)}%</span>
            </div>
          </div>

          {/* Test Details */}
          {testConfig && (
            <Card>
              <CardContent className="p-4 space-y-2">
                <div className="text-sm">
                  <span className="font-medium">Question:</span> {testConfig.question}
                </div>
                <div className="text-sm">
                  <span className="font-medium">URL:</span> {testConfig.url}
                </div>
                {testConfig.selector && (
                  <div className="text-sm">
                    <span className="font-medium">Starting element:</span> {testConfig.selector}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Status Summary */}
          <div className="flex gap-4 text-sm">
            {runningCount > 0 && (
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <span>{runningCount} running</span>
              </div>
            )}
            {completedCount > 0 && (
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>{completedCount} completed</span>
              </div>
            )}
            {failedCount > 0 && (
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                <span>{failedCount} failed</span>
              </div>
            )}
          </div>

          {/* Agent Status */}
          {agents.length > 0 && (
            <div className="space-y-3">
              <h4 className="font-medium">Agent Progress</h4>
              <div className="space-y-2 max-h-64 overflow-auto">
                {agents.map((agent) => (
                  <div key={agent.agent_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Badge className={`${getStatusColor(agent.status)} border`}>
                        <User className="w-3 h-3 mr-1" />
                        {agent.persona}
                      </Badge>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(agent.status)}
                        <span className="text-sm capitalize">{agent.status}</span>
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      {agent.progress}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center gap-2 text-red-700">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm">{error}</span>
              </div>
            </div>
          )}

          {/* Loading State */}
          {agents.length === 0 && !error && (
            <div className="text-center py-8">
              <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-sm text-gray-600">Initializing agents...</p>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}