'use client';

import { useState, useEffect, useRef } from 'react';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { ScrollArea } from './ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { User, Clock, MousePointer, Eye, Type, AlertCircle, Search, Filter } from 'lucide-react';
import { agentApi, interactionApi, Agent, Interaction } from '@/lib/api';

interface TranscriptViewProps {
  testConfig: any;
  onSelectInsight: (step: any) => void;
}

interface InteractionWithAgent extends Interaction {
  agent?: Agent;
  persona?: string;
  color?: string;
}

export function TranscriptView({ testConfig, onSelectInsight }: TranscriptViewProps) {
  const [interactions, setInteractions] = useState<InteractionWithAgent[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [actionFilter, setActionFilter] = useState<string>('all');
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const PERSONA_COLORS = [
    'bg-pink-100 text-pink-700 border-pink-300',
    'bg-blue-100 text-blue-700 border-blue-300',
    'bg-green-100 text-green-700 border-green-300',
    'bg-purple-100 text-purple-700 border-purple-300',
    'bg-orange-100 text-orange-700 border-orange-300',
    'bg-indigo-100 text-indigo-700 border-indigo-300',
    'bg-yellow-100 text-yellow-700 border-yellow-300',
    'bg-teal-100 text-teal-700 border-teal-300',
  ];

  useEffect(() => {
    if (testConfig?.id || testConfig?.runId) {
      loadInteractions();
    }
  }, [testConfig]);

  const loadInteractions = async () => {
    setLoading(true);
    setError(null);

    try {
      const runId = testConfig.id || testConfig.runId;
      
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
          color: PERSONA_COLORS[agentIndex % PERSONA_COLORS.length]
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
  };

  const filteredInteractions = interactions.filter(interaction => {
    // Agent filter
    if (selectedAgent !== 'all' && interaction.agent_id !== selectedAgent) {
      return false;
    }

    // Action type filter
    if (actionFilter !== 'all' && interaction.action_type !== actionFilter) {
      return false;
    }

    // Search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return (
        interaction.intent?.toLowerCase().includes(searchLower) ||
        interaction.result?.toLowerCase().includes(searchLower) ||
        interaction.selector?.toLowerCase().includes(searchLower) ||
        interaction.persona?.toLowerCase().includes(searchLower)
      );
    }

    return true;
  });

  const getActionIcon = (actionType?: string) => {
    switch (actionType) {
      case 'click': return <MousePointer className="w-4 h-4" />;
      case 'type': return <Type className="w-4 h-4" />;
      case 'scroll': return <Eye className="w-4 h-4" />;
      case 'wait': return <Clock className="w-4 h-4" />;
      default: return <MousePointer className="w-4 h-4" />;
    }
  };

  const getActionColor = (actionType?: string) => {
    switch (actionType) {
      case 'click': return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'type': return 'bg-green-50 text-green-700 border-green-200';
      case 'scroll': return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'wait': return 'bg-yellow-50 text-yellow-700 border-yellow-200';
      default: return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  const uniqueActionTypes = [...new Set(interactions.map(i => i.action_type).filter(Boolean))];

  if (loading) {
    return (
      <div className="h-full bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading test transcript...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full bg-white flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={loadInteractions} variant="outline">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-white flex flex-col">
      {/* Header & Filters */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Test Transcript</h2>
          <div className="text-sm text-gray-600">
            {filteredInteractions.length} of {interactions.length} interactions
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Search className="w-4 h-4 text-gray-500" />
            <Input
              placeholder="Search interactions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-64"
            />
          </div>

          <Select value={selectedAgent} onValueChange={setSelectedAgent}>
            <SelectTrigger className="w-48">
              <User className="w-4 h-4 mr-2" />
              <SelectValue placeholder="All agents" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Agents</SelectItem>
              {agents.map((agent, index) => (
                <SelectItem key={agent.agent_id} value={agent.agent_id}>
                  {agent.persona || `Agent ${index + 1}`}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {uniqueActionTypes.length > 0 && (
            <Select value={actionFilter} onValueChange={setActionFilter}>
              <SelectTrigger className="w-48">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="All actions" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Actions</SelectItem>
                {uniqueActionTypes.map(actionType => (
                  <SelectItem key={actionType} value={actionType}>
                    {actionType}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>
      </div>

      {/* Interactions List */}
      <ScrollArea className="flex-1 p-6" ref={scrollAreaRef}>
        {filteredInteractions.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">
              {interactions.length === 0 
                ? 'No interactions found for this test.' 
                : 'No interactions match your current filters.'
              }
            </p>
            {searchTerm || selectedAgent !== 'all' || actionFilter !== 'all' ? (
              <Button 
                variant="outline" 
                onClick={() => {
                  setSearchTerm('');
                  setSelectedAgent('all');
                  setActionFilter('all');
                }}
                className="mt-4"
              >
                Clear Filters
              </Button>
            ) : null}
          </div>
        ) : (
          <div className="space-y-4">
            {filteredInteractions.map((interaction, index) => (
              <Card 
                key={interaction.interaction_id} 
                className="hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => onSelectInsight(interaction)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    {/* Step Number */}
                    <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center text-sm font-medium text-gray-600">
                      {interaction.step}
                    </div>

                    {/* Main Content */}
                    <div className="flex-1 space-y-3">
                      {/* Header with persona and action */}
                      <div className="flex items-center gap-3 flex-wrap">
                        <Badge className={`${interaction.color} border`}>
                          <User className="w-3 h-3 mr-1" />
                          {interaction.persona}
                        </Badge>

                        {interaction.action_type && (
                          <Badge className={`${getActionColor(interaction.action_type)} border`}>
                            {getActionIcon(interaction.action_type)}
                            <span className="ml-1 capitalize">{interaction.action_type}</span>
                          </Badge>
                        )}

                        <span className="text-sm text-gray-500">
                          {formatTimestamp(interaction.created_at)}
                        </span>
                      </div>

                      {/* Intent */}
                      {interaction.intent && (
                        <div>
                          <span className="text-sm font-medium text-gray-700">Intent: </span>
                          <span className="text-sm text-gray-600">{interaction.intent}</span>
                        </div>
                      )}

                      {/* Selector */}
                      {interaction.selector && (
                        <div>
                          <span className="text-sm font-medium text-gray-700">Target: </span>
                          <code className="text-sm bg-gray-100 px-2 py-1 rounded text-gray-800">
                            {interaction.selector}
                          </code>
                        </div>
                      )}

                      {/* Result */}
                      <div>
                        <span className="text-sm font-medium text-gray-700">Result: </span>
                        <span className="text-sm text-gray-600">{interaction.result}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}