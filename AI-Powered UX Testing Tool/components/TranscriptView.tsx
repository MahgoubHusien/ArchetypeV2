import { useState } from 'react';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Switch } from './ui/switch';
import { ScrollArea } from './ui/scroll-area';
import { ChevronDown, ChevronRight, Filter, Users, Target, Brain, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface TranscriptStep {
  id: string;
  agentId: string;
  persona: string;
  personaColor: string;
  timestamp: string;
  intent: string;
  action: string;
  result: string;
  thought: string;
  status: 'success' | 'failure' | 'confusion';
}

interface Agent {
  id: string;
  persona: string;
  personaColor: string;
  status: 'completed' | 'failed' | 'confused';
  steps: number;
}

const mockAgents: Agent[] = [
  { id: '1', persona: 'Etsy mom', personaColor: 'bg-pink-100 text-pink-700', status: 'completed', steps: 8 },
  { id: '2', persona: 'Etsy mom', personaColor: 'bg-pink-100 text-pink-700', status: 'confused', steps: 6 },
  { id: '3', persona: 'SaaS PM', personaColor: 'bg-blue-100 text-blue-700', status: 'completed', steps: 12 },
  { id: '4', persona: 'SaaS PM', personaColor: 'bg-blue-100 text-blue-700', status: 'failed', steps: 4 },
  { id: '5', persona: 'Busy professional', personaColor: 'bg-green-100 text-green-700', status: 'completed', steps: 9 }
];

const mockTranscript: TranscriptStep[] = [
  {
    id: '1',
    agentId: '1',
    persona: 'Etsy mom',
    personaColor: 'bg-pink-100 text-pink-700',
    timestamp: '14:32:01',
    intent: 'Find checkout button',
    action: 'Clicked "Add to Cart" button',
    result: 'Successfully added item to cart',
    thought: 'The button was clearly visible and accessible',
    status: 'success'
  },
  {
    id: '2',
    agentId: '2',
    persona: 'Etsy mom',
    personaColor: 'bg-pink-100 text-pink-700',
    timestamp: '14:32:15',
    intent: 'Proceed to checkout',
    action: 'Looking for checkout button',
    result: 'Could not locate checkout button immediately',
    thought: 'Expected button to be more prominent, had to search',
    status: 'confusion'
  },
  {
    id: '3',
    agentId: '3',
    persona: 'SaaS PM',
    personaColor: 'bg-blue-100 text-blue-700',
    timestamp: '14:32:18',
    intent: 'Review cart contents',
    action: 'Scrolled through cart page',
    result: 'Successfully reviewed items and quantities',
    thought: 'Cart layout is clear and well organized',
    status: 'success'
  },
  {
    id: '4',
    agentId: '4',
    persona: 'SaaS PM',
    personaColor: 'bg-blue-100 text-blue-700',
    timestamp: '14:32:25',
    intent: 'Apply discount code',
    action: 'Clicked "Promo Code" field',
    result: 'Field appeared but validation failed',
    thought: 'Error message was unclear about what went wrong',
    status: 'failure'
  }
];

interface TranscriptViewProps {
  testConfig: any;
  onSelectInsight: (step: TranscriptStep) => void;
}

export function TranscriptView({ testConfig, onSelectInsight }: TranscriptViewProps) {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());
  const [selectedPersona, setSelectedPersona] = useState<string>('all');
  const [confusionFilter, setConfusionFilter] = useState<string>('all');
  const [showFailedOnly, setShowFailedOnly] = useState(false);

  const toggleStep = (stepId: string) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(stepId)) {
      newExpanded.delete(stepId);
    } else {
      newExpanded.add(stepId);
    }
    setExpandedSteps(newExpanded);
  };

  const filteredTranscript = mockTranscript.filter(step => {
    if (selectedPersona !== 'all' && step.persona !== selectedPersona) return false;
    if (confusionFilter !== 'all' && step.status !== confusionFilter) return false;
    if (showFailedOnly && step.status === 'success') return false;
    return true;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <div className="w-2 h-2 bg-green-500 rounded-full" />;
      case 'failure':
        return <div className="w-2 h-2 bg-red-500 rounded-full" />;
      case 'confusion':
        return <div className="w-2 h-2 bg-yellow-500 rounded-full" />;
      default:
        return <div className="w-2 h-2 bg-gray-400 rounded-full" />;
    }
  };

  return (
    <div className="flex h-full bg-[#FAFAFA]">
      {/* Left: Agent List */}
      <div className="w-64 bg-white border-r border-[#E3E3E3] flex flex-col">
        <div className="p-4 border-b border-[#E3E3E3]">
          <h3 className="text-[#1A1A1A] mb-2">Agents</h3>
          <p className="text-sm text-[#555]">{mockAgents.length} agents running</p>
        </div>
        
        <ScrollArea className="flex-1">
          <div className="p-4">
            {/* Group by persona */}
            {Array.from(new Set(mockAgents.map(a => a.persona))).map(persona => (
              <div key={persona} className="mb-4">
                <div className="text-sm text-[#555] mb-2">{persona}</div>
                <div className="space-y-2">
                  {mockAgents.filter(a => a.persona === persona).map(agent => (
                    <motion.button
                      key={agent.id}
                      onClick={() => setSelectedAgent(agent.id)}
                      className={`w-full p-3 rounded-lg border text-left transition-colors ${
                        selectedAgent === agent.id 
                          ? 'border-[#4F46E5] bg-[#F0F0FF]' 
                          : 'border-[#E3E3E3] hover:bg-[#F3F3F5]'
                      }`}
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <Badge className={`${agent.personaColor} border-none text-xs`}>
                          Agent {agent.id}
                        </Badge>
                        {getStatusIcon(agent.status)}
                      </div>
                      <div className="text-xs text-[#555]">{agent.steps} steps</div>
                    </motion.button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Middle: Transcript */}
      <div className="flex-1 flex flex-col">
        <div className="p-4 border-b border-[#E3E3E3] bg-white">
          <h2 className="text-[#1A1A1A] mb-4">Test Transcript</h2>
          
          {/* Filters */}
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-[#555]" />
              <span className="text-[#555]">Filters:</span>
            </div>
            
            <Select value={selectedPersona} onValueChange={setSelectedPersona}>
              <SelectTrigger className="w-40 bg-[#F3F3F5] border-[#E3E3E3]">
                <SelectValue placeholder="All personas" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All personas</SelectItem>
                <SelectItem value="Etsy mom">Etsy mom</SelectItem>
                <SelectItem value="SaaS PM">SaaS PM</SelectItem>
                <SelectItem value="Busy professional">Busy professional</SelectItem>
              </SelectContent>
            </Select>

            <Select value={confusionFilter} onValueChange={setConfusionFilter}>
              <SelectTrigger className="w-40 bg-[#F3F3F5] border-[#E3E3E3]">
                <SelectValue placeholder="All types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All types</SelectItem>
                <SelectItem value="success">Success</SelectItem>
                <SelectItem value="confusion">Confusion</SelectItem>
                <SelectItem value="failure">Failure</SelectItem>
              </SelectContent>
            </Select>

            <div className="flex items-center gap-2">
              <Switch
                checked={showFailedOnly}
                onCheckedChange={setShowFailedOnly}
              />
              <span className="text-[#555]">Failed paths only</span>
            </div>
          </div>
        </div>

        <ScrollArea className="flex-1 p-4">
          <div className="space-y-3">
            <AnimatePresence>
              {filteredTranscript.map((step) => (
                <motion.div
                  key={step.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="bg-white rounded-lg border border-[#E3E3E3] overflow-hidden"
                >
                  <button
                    onClick={() => toggleStep(step.id)}
                    className="w-full p-4 text-left hover:bg-[#F3F3F5] transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {expandedSteps.has(step.id) ? (
                          <ChevronDown className="w-4 h-4 text-[#555]" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-[#555]" />
                        )}
                        {getStatusIcon(step.status)}
                        <Badge className={`${step.personaColor} border-none text-xs`}>
                          {step.persona}
                        </Badge>
                        <span className="text-[#1A1A1A]">{step.intent}</span>
                      </div>
                      <span className="text-xs text-[#555]">{step.timestamp}</span>
                    </div>
                  </button>

                  <AnimatePresence>
                    {expandedSteps.has(step.id) && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="border-t border-[#E3E3E3] bg-[#F9F9F9]"
                      >
                        <div className="p-4 space-y-3">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <div className="flex items-center gap-2 mb-1">
                                <Target className="w-4 h-4 text-[#555]" />
                                <span className="text-sm text-[#555]">Action</span>
                              </div>
                              <p className="text-sm text-[#1A1A1A]">{step.action}</p>
                            </div>
                            <div>
                              <div className="flex items-center gap-2 mb-1">
                                <AlertCircle className="w-4 h-4 text-[#555]" />
                                <span className="text-sm text-[#555]">Result</span>
                              </div>
                              <p className="text-sm text-[#1A1A1A]">{step.result}</p>
                            </div>
                          </div>
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <Brain className="w-4 h-4 text-[#555]" />
                              <span className="text-sm text-[#555]">Agent Thought</span>
                            </div>
                            <p className="text-sm text-[#555] italic">"{step.thought}"</p>
                          </div>
                          <Button
                            onClick={() => onSelectInsight(step)}
                            size="sm"
                            className="bg-[#E9EBEF] text-[#1A1A1A] hover:bg-[#CBCED4] border-none"
                          >
                            Jump to Insights
                          </Button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </ScrollArea>
      </div>

      {/* Right: Context Sidebar */}
      <div className="w-64 bg-white border-l border-[#E3E3E3] p-4">
        <div className="space-y-4">
          <div>
            <h4 className="text-[#1A1A1A] mb-2">Test Context</h4>
            <div className="space-y-2">
              <div className="p-3 bg-[#F3F3F5] rounded-lg">
                <div className="text-xs text-[#555] mb-1">Question</div>
                <p className="text-sm text-[#1A1A1A]">{testConfig?.question || 'Where do users get confused during checkout?'}</p>
              </div>
              <div className="p-3 bg-[#F3F3F5] rounded-lg">
                <div className="text-xs text-[#555] mb-1">Target URL</div>
                <p className="text-sm text-[#1A1A1A] break-all">{testConfig?.url || 'https://example.com/checkout'}</p>
              </div>
            </div>
          </div>

          <div>
            <h4 className="text-[#1A1A1A] mb-2 flex items-center gap-2">
              <Users className="w-4 h-4" />
              Personas
            </h4>
            <div className="space-y-2">
              {testConfig?.personas?.map((persona: any, idx: number) => (
                <Badge key={idx} className={`${persona.color} border-none text-xs block w-full justify-start`}>
                  {persona.name}, {persona.age}
                </Badge>
              )) || (
                <>
                  <Badge className="bg-pink-100 text-pink-700 border-none text-xs block w-full justify-start">
                    Etsy mom, 38
                  </Badge>
                  <Badge className="bg-blue-100 text-blue-700 border-none text-xs block w-full justify-start">
                    SaaS PM, 27
                  </Badge>
                  <Badge className="bg-green-100 text-green-700 border-none text-xs block w-full justify-start">
                    Busy professional, 34
                  </Badge>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}