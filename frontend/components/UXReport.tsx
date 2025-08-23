'use client';

import { useState, useEffect } from 'react';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ScrollArea } from './ui/scroll-area';
import { Separator } from './ui/separator';
import { Progress } from './ui/progress';
import { 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  TrendingUp, 
  Users, 
  MousePointer,
  Eye,
  Lightbulb,
  FileText,
  ExternalLink,
  AlertCircle,
  BarChart3,
  Timer
} from 'lucide-react';
import { agentApi, interactionApi, Agent, Interaction } from '@/lib/api';

interface UXReportProps {
  testConfig: any;
  onGenerateTicket: (insight: any) => void;
  onJumpToTranscript: (moment: string) => void;
}

interface UXInsight {
  id: string;
  type: 'issue' | 'success' | 'improvement' | 'observation';
  severity: 'low' | 'medium' | 'high';
  title: string;
  description: string;
  persona: string;
  personaColor: string;
  step: number;
  interactions: Interaction[];
  recommendation?: string;
  impact?: string;
  evidence?: string;
}

interface AnalysisMetrics {
  totalInteractions: number;
  averageSteps: number;
  completionRate: number;
  averageTime: number;
  failurePoints: string[];
  successPatterns: string[];
}

export function UXReport({ testConfig, onGenerateTicket, onJumpToTranscript }: UXReportProps) {
  const [insights, setInsights] = useState<UXInsight[]>([]);
  const [metrics, setMetrics] = useState<AnalysisMetrics | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<string>('all');

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
      loadAnalysisData();
    }
  }, [testConfig]);

  const loadAnalysisData = async () => {
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
      
      // Analyze data and generate insights
      const analysisResults = analyzeInteractions(agentData, interactionResponses);
      setInsights(analysisResults.insights);
      setMetrics(analysisResults.metrics);

    } catch (err) {
      console.error('Error loading analysis data:', err);
      setError('Failed to load UX analysis');
    } finally {
      setLoading(false);
    }
  };

  const analyzeInteractions = (agentData: Agent[], interactionResponses: any[]): {
    insights: UXInsight[],
    metrics: AnalysisMetrics
  } => {
    const allInteractions: Array<Interaction & { agent: Agent; persona: string; color: string }> = [];
    const insights: UXInsight[] = [];

    // Combine all interactions with agent context
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

    // Sort interactions by step
    allInteractions.sort((a, b) => a.step - b.step);

    // Generate metrics
    const completedAgents = agentData.filter(a => a.status === 'completed').length;
    const failedAgents = agentData.filter(a => a.status === 'failed').length;
    const totalAgents = agentData.length;

    // Calculate average steps per agent
    const agentSteps = agentData.map(agent => {
      const agentInteractions = allInteractions.filter(i => i.agent_id === agent.agent_id);
      return agentInteractions.length > 0 ? Math.max(...agentInteractions.map(i => i.step)) : 0;
    });
    const averageSteps = agentSteps.reduce((a, b) => a + b, 0) / agentSteps.length || 0;

    // Calculate average time (mock data for now)
    const averageTime = 45; // seconds - would be calculated from actual timestamps

    const metrics: AnalysisMetrics = {
      totalInteractions: allInteractions.length,
      averageSteps,
      completionRate: totalAgents > 0 ? (completedAgents / totalAgents) * 100 : 0,
      averageTime,
      failurePoints: [], // Would analyze failure patterns
      successPatterns: [] // Would analyze success patterns
    };

    // Generate insights based on analysis
    
    // 1. Completion rate insights
    if (metrics.completionRate < 80) {
      insights.push({
        id: 'completion-rate',
        type: 'issue',
        severity: 'high',
        title: 'Low Task Completion Rate',
        description: `Only ${completedAgents} out of ${totalAgents} agents completed the task successfully (${Math.round(metrics.completionRate)}%).`,
        persona: 'Overall',
        personaColor: 'bg-gray-100 text-gray-700 border-gray-300',
        step: 0,
        interactions: [],
        recommendation: 'Review the user flow for common drop-off points and simplify complex steps.',
        impact: 'High impact on user satisfaction and business goals.',
        evidence: `${failedAgents} agents failed to complete the task.`
      });
    } else {
      insights.push({
        id: 'completion-success',
        type: 'success',
        severity: 'low',
        title: 'High Task Completion Rate',
        description: `${completedAgents} out of ${totalAgents} agents completed the task successfully (${Math.round(metrics.completionRate)}%).`,
        persona: 'Overall',
        personaColor: 'bg-gray-100 text-gray-700 border-gray-300',
        step: 0,
        interactions: [],
        recommendation: 'Maintain current design patterns and consider applying them to other flows.',
        impact: 'Positive indicator of good user experience design.',
        evidence: `${completedAgents} successful completions out of ${totalAgents} attempts.`
      });
    }

    // 2. Step complexity insights
    if (averageSteps > 10) {
      insights.push({
        id: 'complex-flow',
        type: 'improvement',
        severity: 'medium',
        title: 'Complex User Flow',
        description: `Users need an average of ${Math.round(averageSteps)} steps to complete the task.`,
        persona: 'Overall',
        personaColor: 'bg-gray-100 text-gray-700 border-gray-300',
        step: 0,
        interactions: [],
        recommendation: 'Consider streamlining the user flow by combining steps or providing shortcuts.',
        impact: 'Reducing steps could improve user satisfaction and reduce abandonment.',
        evidence: `Average of ${Math.round(averageSteps)} interactions per user.`
      });
    }

    // 3. Analyze per-agent issues
    agentData.forEach((agent, index) => {
      const agentInteractions = allInteractions.filter(i => i.agent_id === agent.agent_id);
      const persona = agent.persona || `Agent ${index + 1}`;
      const color = PERSONA_COLORS[index % PERSONA_COLORS.length];

      if (agent.status === 'failed') {
        const lastInteraction = agentInteractions[agentInteractions.length - 1];
        insights.push({
          id: `failure-${agent.agent_id}`,
          type: 'issue',
          severity: 'high',
          title: `${persona} Failed to Complete Task`,
          description: `This agent encountered an issue and couldn't complete the task.`,
          persona,
          personaColor: color,
          step: lastInteraction?.step || 0,
          interactions: agentInteractions,
          recommendation: 'Investigate the specific failure point and improve error handling or user guidance.',
          impact: 'Failure indicates potential usability issues for this user type.',
          evidence: `Agent failed at step ${lastInteraction?.step || 'unknown'}.`
        });
      }

      // Look for patterns in interactions
      const clickActions = agentInteractions.filter(i => i.action_type === 'click');
      if (clickActions.length > averageSteps * 0.7) {
        insights.push({
          id: `click-heavy-${agent.agent_id}`,
          type: 'observation',
          severity: 'low',
          title: `${persona} Required Many Clicks`,
          description: `This agent performed ${clickActions.length} click actions, suggesting possible navigation difficulties.`,
          persona,
          personaColor: color,
          step: 0,
          interactions: clickActions,
          recommendation: 'Consider improving navigation flow or providing clearer visual hierarchy.',
          impact: 'May indicate suboptimal information architecture.',
          evidence: `${clickActions.length} click actions out of ${agentInteractions.length} total interactions.`
        });
      }
    });

    // 4. Common action patterns
    const allActionTypes = allInteractions.map(i => i.action_type).filter(Boolean);
    const actionCounts = allActionTypes.reduce((acc: Record<string, number>, action) => {
      acc[action] = (acc[action] || 0) + 1;
      return acc;
    }, {});

    const mostCommonAction = Object.entries(actionCounts).reduce((a, b) => 
      actionCounts[a[0]] > actionCounts[b[0]] ? a : b
    );

    if (mostCommonAction && actionCounts[mostCommonAction[0]] > allInteractions.length * 0.4) {
      insights.push({
        id: 'dominant-action',
        type: 'observation',
        severity: 'low',
        title: `Heavy Reliance on ${mostCommonAction[0]} Actions`,
        description: `${mostCommonAction[1]} out of ${allInteractions.length} interactions were ${mostCommonAction[0]} actions.`,
        persona: 'Overall',
        personaColor: 'bg-gray-100 text-gray-700 border-gray-300',
        step: 0,
        interactions: [],
        recommendation: `Review if the prevalence of ${mostCommonAction[0]} actions indicates an interaction design issue.`,
        impact: 'May suggest opportunities for interaction optimization.',
        evidence: `${mostCommonAction[1]} ${mostCommonAction[0]} actions observed.`
      });
    }

    return { insights, metrics };
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'issue': return <AlertTriangle className="w-5 h-5 text-red-600" />;
      case 'success': return <CheckCircle2 className="w-5 h-5 text-green-600" />;
      case 'improvement': return <TrendingUp className="w-5 h-5 text-blue-600" />;
      case 'observation': return <Eye className="w-5 h-5 text-purple-600" />;
      default: return <Lightbulb className="w-5 h-5 text-gray-600" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const filteredInsights = insights.filter(insight => 
    activeFilter === 'all' || insight.type === activeFilter
  );

  const insightCounts = {
    all: insights.length,
    issue: insights.filter(i => i.type === 'issue').length,
    success: insights.filter(i => i.type === 'success').length,
    improvement: insights.filter(i => i.type === 'improvement').length,
    observation: insights.filter(i => i.type === 'observation').length,
  };

  if (loading) {
    return (
      <div className="h-full bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Analyzing test results...</p>
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
          <Button onClick={loadAnalysisData} variant="outline">
            Retry Analysis
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-white flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-semibold mb-4">UX Analysis Report</h2>
        
        {/* Metrics Overview */}
        {metrics && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardContent className="p-4 text-center">
                <div className="flex items-center justify-center mb-2">
                  <Users className="w-5 h-5 text-blue-600" />
                </div>
                <div className="text-2xl font-bold text-blue-600">{Math.round(metrics.completionRate)}%</div>
                <div className="text-sm text-gray-600">Completion Rate</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4 text-center">
                <div className="flex items-center justify-center mb-2">
                  <BarChart3 className="w-5 h-5 text-green-600" />
                </div>
                <div className="text-2xl font-bold text-green-600">{Math.round(metrics.averageSteps)}</div>
                <div className="text-sm text-gray-600">Avg Steps</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4 text-center">
                <div className="flex items-center justify-center mb-2">
                  <Timer className="w-5 h-5 text-purple-600" />
                </div>
                <div className="text-2xl font-bold text-purple-600">{metrics.averageTime}s</div>
                <div className="text-sm text-gray-600">Avg Time</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4 text-center">
                <div className="flex items-center justify-center mb-2">
                  <MousePointer className="w-5 h-5 text-orange-600" />
                </div>
                <div className="text-2xl font-bold text-orange-600">{metrics.totalInteractions}</div>
                <div className="text-sm text-gray-600">Interactions</div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Filter Tabs */}
        <div className="flex gap-2 flex-wrap">
          {Object.entries(insightCounts).map(([type, count]) => (
            <Button
              key={type}
              variant={activeFilter === type ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActiveFilter(type)}
              className="capitalize"
            >
              {type} ({count})
            </Button>
          ))}
        </div>
      </div>

      {/* Insights List */}
      <ScrollArea className="flex-1 p-6">
        {filteredInsights.length === 0 ? (
          <div className="text-center py-12">
            <Lightbulb className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">
              {insights.length === 0 
                ? 'No insights generated yet.' 
                : 'No insights match your current filter.'
              }
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {filteredInsights.map((insight) => (
              <Card key={insight.id} className="shadow-sm hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3">
                      {getInsightIcon(insight.type)}
                      <div>
                        <CardTitle className="text-lg">{insight.title}</CardTitle>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge className={`${insight.personaColor} border`}>
                            <User className="w-3 h-3 mr-1" />
                            {insight.persona}
                          </Badge>
                          <Badge className={`${getSeverityColor(insight.severity)} border`}>
                            {insight.severity} severity
                          </Badge>
                          {insight.step > 0 && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => onJumpToTranscript(`step-${insight.step}`)}
                              className="text-xs"
                            >
                              <ExternalLink className="w-3 h-3 mr-1" />
                              Step {insight.step}
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                    <Button
                      onClick={() => onGenerateTicket(insight)}
                      variant="outline"
                      size="sm"
                    >
                      <FileText className="w-4 h-4 mr-2" />
                      Create Ticket
                    </Button>
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <p className="text-gray-700">{insight.description}</p>
                  
                  {insight.evidence && (
                    <div>
                      <h4 className="font-medium text-sm text-gray-900 mb-1">Evidence</h4>
                      <p className="text-sm text-gray-600">{insight.evidence}</p>
                    </div>
                  )}
                  
                  {insight.recommendation && (
                    <div>
                      <h4 className="font-medium text-sm text-gray-900 mb-1">Recommendation</h4>
                      <p className="text-sm text-gray-600">{insight.recommendation}</p>
                    </div>
                  )}
                  
                  {insight.impact && (
                    <div>
                      <h4 className="font-medium text-sm text-gray-900 mb-1">Impact</h4>
                      <p className="text-sm text-gray-600">{insight.impact}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}