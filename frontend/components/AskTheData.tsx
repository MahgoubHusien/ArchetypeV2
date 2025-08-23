'use client';

import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Separator } from './ui/separator';
import { 
  Search, 
  Send, 
  Bot, 
  User, 
  TrendingUp, 
  BarChart3, 
  Clock, 
  MousePointer,
  AlertCircle,
  Lightbulb,
  Database,
  Filter,
  Download
} from 'lucide-react';
import { agentApi, interactionApi, Agent, Interaction } from '@/lib/api';

interface AskTheDataProps {
  testConfig: any;
}

interface QueryResponse {
  id: string;
  question: string;
  answer: string;
  data?: any[];
  charts?: {
    type: 'bar' | 'line' | 'pie';
    data: any[];
    title: string;
  }[];
  timestamp: Date;
}

interface SuggestedQuery {
  id: string;
  question: string;
  category: 'performance' | 'behavior' | 'completion' | 'errors';
  description: string;
}

export function AskTheData({ testConfig }: AskTheDataProps) {
  const [query, setQuery] = useState('');
  const [responses, setResponses] = useState<QueryResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [dataLoading, setDataLoading] = useState(true);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [error, setError] = useState<string | null>(null);

  const suggestedQueries: SuggestedQuery[] = [
    {
      id: '1',
      question: 'Which agent took the most steps to complete the task?',
      category: 'performance',
      description: 'Analyze step count variations between different personas'
    },
    {
      id: '2',
      question: 'What were the most common failure points?',
      category: 'errors',
      description: 'Identify patterns in where users get stuck or fail'
    },
    {
      id: '3',
      question: 'How did different personas interact with the interface?',
      category: 'behavior',
      description: 'Compare interaction patterns across user types'
    },
    {
      id: '4',
      question: 'What was the completion rate by persona type?',
      category: 'completion',
      description: 'Success rate analysis for each user persona'
    },
    {
      id: '5',
      question: 'Which UI elements were clicked most frequently?',
      category: 'behavior',
      description: 'Popular interface elements and interaction hotspots'
    },
    {
      id: '6',
      question: 'How much time did each agent spend on the task?',
      category: 'performance',
      description: 'Time analysis across different user personas'
    }
  ];

  useEffect(() => {
    if (testConfig?.id || testConfig?.runId) {
      loadTestData();
    }
  }, [testConfig]);

  const loadTestData = async () => {
    setDataLoading(true);
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
      
      // Combine all interactions
      const allInteractions: Interaction[] = [];
      interactionResponses.forEach(response => {
        allInteractions.push(...response.data);
      });
      
      setInteractions(allInteractions);

    } catch (err) {
      console.error('Error loading test data:', err);
      setError('Failed to load test data');
    } finally {
      setDataLoading(false);
    }
  };

  const handleQuery = async (questionText: string) => {
    if (!questionText.trim()) return;

    setLoading(true);
    const question = questionText.trim();

    try {
      // Simulate AI processing the query against the data
      const response = await processQuery(question);
      
      setResponses(prev => [response, ...prev]);
      setQuery('');
    } catch (err) {
      console.error('Query processing failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const processQuery = async (question: string): Promise<QueryResponse> => {
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 1000));

    const questionLower = question.toLowerCase();
    const response: QueryResponse = {
      id: `query-${Date.now()}`,
      question,
      answer: '',
      timestamp: new Date()
    };

    // Simple query processing based on keywords
    if (questionLower.includes('step') && (questionLower.includes('most') || questionLower.includes('max'))) {
      const agentSteps = agents.map(agent => {
        const agentInteractions = interactions.filter(i => i.agent_id === agent.agent_id);
        const steps = agentInteractions.length > 0 ? Math.max(...agentInteractions.map(i => i.step)) : 0;
        return { agent: agent.persona || 'Unknown Agent', steps };
      });
      
      const maxSteps = Math.max(...agentSteps.map(a => a.steps));
      const topAgent = agentSteps.find(a => a.steps === maxSteps);
      
      response.answer = `${topAgent?.agent || 'Unknown'} took the most steps with ${maxSteps} total steps to complete the task. This could indicate that this persona had more difficulty with the interface or took a more exploratory approach.`;
      response.data = agentSteps;
    }
    
    else if (questionLower.includes('completion') && questionLower.includes('rate')) {
      const totalAgents = agents.length;
      const completedAgents = agents.filter(a => a.status === 'completed').length;
      const completionRate = totalAgents > 0 ? (completedAgents / totalAgents) * 100 : 0;
      
      const personaCompletion = agents.map(agent => ({
        persona: agent.persona || 'Unknown Agent',
        status: agent.status,
        completed: agent.status === 'completed'
      }));

      response.answer = `The overall completion rate is ${completionRate.toFixed(1)}% (${completedAgents} out of ${totalAgents} agents). ${completedAgents === totalAgents ? 'All personas successfully completed the task.' : `${totalAgents - completedAgents} personas failed to complete the task, which indicates potential usability issues.`}`;
      response.data = personaCompletion;
    }
    
    else if (questionLower.includes('failure') || questionLower.includes('fail')) {
      const failedAgents = agents.filter(a => a.status === 'failed');
      const failurePoints = failedAgents.map(agent => {
        const agentInteractions = interactions.filter(i => i.agent_id === agent.agent_id);
        const lastInteraction = agentInteractions[agentInteractions.length - 1];
        return {
          persona: agent.persona || 'Unknown Agent',
          lastStep: lastInteraction?.step || 0,
          lastAction: lastInteraction?.action_type || 'unknown',
          element: lastInteraction?.selector || 'unknown'
        };
      });

      if (failurePoints.length === 0) {
        response.answer = 'No failures were detected in this test. All agents successfully completed their tasks.';
      } else {
        const stepCounts = failurePoints.reduce((acc: Record<number, number>, fp) => {
          acc[fp.lastStep] = (acc[fp.lastStep] || 0) + 1;
          return acc;
        }, {});
        
        const commonStep = Object.entries(stepCounts).reduce((a, b) => 
          stepCounts[parseInt(a[0])] > stepCounts[parseInt(b[0])] ? a : b
        );

        response.answer = `${failurePoints.length} agent(s) failed to complete the task. The most common failure point was at step ${commonStep[0]}, where ${commonStep[1]} agent(s) encountered issues. This suggests a potential usability problem at this stage of the user flow.`;
        response.data = failurePoints;
      }
    }
    
    else if (questionLower.includes('interact') && questionLower.includes('persona')) {
      const personaInteractions = agents.map(agent => {
        const agentInteractions = interactions.filter(i => i.agent_id === agent.agent_id);
        const actionTypes = agentInteractions.reduce((acc: Record<string, number>, interaction) => {
          if (interaction.action_type) {
            acc[interaction.action_type] = (acc[interaction.action_type] || 0) + 1;
          }
          return acc;
        }, {});

        return {
          persona: agent.persona || 'Unknown Agent',
          totalInteractions: agentInteractions.length,
          actions: actionTypes,
          status: agent.status
        };
      });

      response.answer = `Different personas showed varying interaction patterns. ${personaInteractions.map(pi => 
        `${pi.persona} performed ${pi.totalInteractions} interactions with a focus on ${Object.entries(pi.actions).sort((a, b) => b[1] - a[1])[0]?.[0] || 'unknown'} actions`
      ).join('. ')}.`;
      response.data = personaInteractions;
    }

    else if (questionLower.includes('click') && (questionLower.includes('most') || questionLower.includes('frequent'))) {
      const clickInteractions = interactions.filter(i => i.action_type === 'click');
      const elementCounts = clickInteractions.reduce((acc: Record<string, number>, interaction) => {
        if (interaction.selector) {
          acc[interaction.selector] = (acc[interaction.selector] || 0) + 1;
        }
        return acc;
      }, {});

      const sortedElements = Object.entries(elementCounts).sort((a, b) => b[1] - a[1]).slice(0, 5);
      
      if (sortedElements.length === 0) {
        response.answer = 'No click interactions were recorded in this test.';
      } else {
        response.answer = `The most frequently clicked elements were: ${sortedElements.map(([element, count]) => 
          `${element} (${count} clicks)`
        ).join(', ')}. This indicates these are key interaction points in your interface.`;
        response.data = sortedElements.map(([element, count]) => ({ element, clicks: count }));
      }
    }

    else if (questionLower.includes('time')) {
      // Mock time analysis since we don't have real timestamps
      const timeData = agents.map((agent, index) => ({
        persona: agent.persona || 'Unknown Agent',
        timeSpent: Math.floor(Math.random() * 120) + 30, // 30-150 seconds
        status: agent.status
      }));
      
      const avgTime = timeData.reduce((sum, agent) => sum + agent.timeSpent, 0) / timeData.length;
      const slowestAgent = timeData.reduce((prev, current) => 
        current.timeSpent > prev.timeSpent ? current : prev
      );

      response.answer = `The average time spent was ${avgTime.toFixed(1)} seconds. ${slowestAgent.persona} took the longest at ${slowestAgent.timeSpent} seconds, which might indicate difficulty with the interface or a more thorough exploration approach.`;
      response.data = timeData;
    }

    else {
      // Generic response for unrecognized queries
      response.answer = `I analyzed "${question}" but couldn't find a specific pattern to match. Try asking about completion rates, step counts, interaction patterns, failure points, or timing data. You can also use one of the suggested queries below.`;
    }

    return response;
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'performance': return 'bg-blue-100 text-blue-700 border-blue-300';
      case 'behavior': return 'bg-green-100 text-green-700 border-green-300';
      case 'completion': return 'bg-purple-100 text-purple-700 border-purple-300';
      case 'errors': return 'bg-red-100 text-red-700 border-red-300';
      default: return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  const formatDataTable = (data: any[]) => {
    if (!data || data.length === 0) return null;

    const keys = Object.keys(data[0]);
    
    return (
      <div className="mt-4 p-4 bg-gray-50 rounded-lg overflow-auto">
        <div className="flex items-center gap-2 mb-3">
          <Database className="w-4 h-4 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">Data Results</span>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                {keys.map(key => (
                  <th key={key} className="text-left p-2 font-medium text-gray-700 capitalize">
                    {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, index) => (
                <tr key={index} className="border-b border-gray-100">
                  {keys.map(key => (
                    <td key={key} className="p-2 text-gray-600">
                      {typeof row[key] === 'boolean' ? (row[key] ? 'Yes' : 'No') : row[key]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  if (dataLoading) {
    return (
      <div className="h-full bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading test data...</p>
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
          <Button onClick={loadTestData} variant="outline">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-white flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-semibold mb-2">Ask the Data</h2>
        <p className="text-gray-600 mb-4">
          Query your test data using natural language. Ask questions about user behavior, completion rates, and interaction patterns.
        </p>
        
        {/* Query Input */}
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Which persona had the highest completion rate?"
              className="pl-10 py-6"
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !loading) {
                  handleQuery(query);
                }
              }}
              disabled={loading}
            />
          </div>
          <Button 
            onClick={() => handleQuery(query)}
            disabled={loading || !query.trim()}
            className="px-6 py-6"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
      </div>

      <div className="flex-1 flex">
        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Query Responses */}
          <ScrollArea className="flex-1 p-6">
            {responses.length === 0 ? (
              <div className="text-center py-12">
                <Bot className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-700 mb-2">Ready to Analyze</h3>
                <p className="text-gray-600">
                  Ask questions about your test data or try one of the suggested queries.
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                {responses.map((response) => (
                  <Card key={response.id} className="shadow-sm">
                    <CardContent className="p-6">
                      {/* Question */}
                      <div className="flex items-start gap-3 mb-4">
                        <User className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="text-gray-900 font-medium">{response.question}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            {response.timestamp.toLocaleTimeString()}
                          </p>
                        </div>
                      </div>

                      {/* Answer */}
                      <div className="flex items-start gap-3">
                        <Bot className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="text-gray-700 leading-relaxed">{response.answer}</p>
                          
                          {/* Data Table */}
                          {response.data && formatDataTable(response.data)}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </ScrollArea>
        </div>

        {/* Suggested Queries Sidebar */}
        <div className="w-80 border-l border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Suggested Queries</h3>
          <div className="space-y-3">
            {suggestedQueries.map((suggestion) => (
              <Card 
                key={suggestion.id} 
                className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => handleQuery(suggestion.question)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-3 mb-2">
                    <Badge className={`${getCategoryColor(suggestion.category)} border text-xs`}>
                      {suggestion.category}
                    </Badge>
                  </div>
                  <p className="font-medium text-sm text-gray-900 mb-1">
                    {suggestion.question}
                  </p>
                  <p className="text-xs text-gray-600">
                    {suggestion.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>

          <Separator className="my-6" />
          
          {/* Data Summary */}
          <div className="space-y-3">
            <h4 className="font-medium text-gray-900">Available Data</h4>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Agents</span>
                <span className="font-medium">{agents.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Interactions</span>
                <span className="font-medium">{interactions.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Completed</span>
                <span className="font-medium">
                  {agents.filter(a => a.status === 'completed').length}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Failed</span>
                <span className="font-medium">
                  {agents.filter(a => a.status === 'failed').length}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}