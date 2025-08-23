import { useState } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ScrollArea } from './ui/scroll-area';
import { Lightbulb, AlertTriangle, CheckCircle, ExternalLink, FileText, Users, TrendingUp } from 'lucide-react';
import { motion } from 'motion/react';

interface Insight {
  id: string;
  type: 'confusion' | 'blocker' | 'success' | 'suggestion';
  title: string;
  description: string;
  severity: 'high' | 'medium' | 'low';
  personas: string[];
  personaColors: string[];
  transcriptMoment?: string;
  suggestions: string[];
}

const mockInsights: Insight[] = [
  {
    id: '1',
    type: 'confusion',
    title: 'Checkout button visibility issues',
    description: 'Multiple users struggled to locate the primary checkout button, spending 15-30 seconds searching.',
    severity: 'high',
    personas: ['Etsy mom', 'Busy professional'],
    personaColors: ['bg-pink-100 text-pink-700', 'bg-green-100 text-green-700'],
    transcriptMoment: '14:32:15',
    suggestions: [
      'Increase button size and contrast ratio',
      'Position checkout button above the fold',
      'Use more prominent CTA color scheme'
    ]
  },
  {
    id: '2',
    type: 'blocker',
    title: 'Promo code validation errors',
    description: 'Error messages were unclear, causing users to abandon the checkout process.',
    severity: 'high',
    personas: ['SaaS PM'],
    personaColors: ['bg-blue-100 text-blue-700'],
    transcriptMoment: '14:32:25',
    suggestions: [
      'Provide specific error messages',
      'Show valid promo code format examples',
      'Add real-time validation feedback'
    ]
  },
  {
    id: '3',
    type: 'success',
    title: 'Cart review process works well',
    description: 'Users easily understood cart contents and could modify quantities without confusion.',
    severity: 'low',
    personas: ['SaaS PM', 'Busy professional'],
    personaColors: ['bg-blue-100 text-blue-700', 'bg-green-100 text-green-700'],
    suggestions: [
      'Consider using this layout pattern elsewhere',
      'Maintain current clear labeling system'
    ]
  },
  {
    id: '4',
    type: 'suggestion',
    title: 'Mobile optimization opportunities',
    description: 'Touch targets could be larger for improved mobile experience.',
    severity: 'medium',
    personas: ['Etsy mom'],
    personaColors: ['bg-pink-100 text-pink-700'],
    suggestions: [
      'Increase button size to 44px minimum',
      'Add more spacing between interactive elements',
      'Test with actual mobile devices'
    ]
  }
];

interface UXReportProps {
  testConfig: any;
  onGenerateTicket: (insight: Insight) => void;
  onJumpToTranscript: (moment: string) => void;
}

export function UXReport({ testConfig, onGenerateTicket, onJumpToTranscript }: UXReportProps) {
  const [selectedInsight, setSelectedInsight] = useState<string | null>(null);

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'confusion':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      case 'blocker':
        return <AlertTriangle className="w-5 h-5 text-red-600" />;
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'suggestion':
        return <Lightbulb className="w-5 h-5 text-blue-600" />;
      default:
        return <Lightbulb className="w-5 h-5 text-gray-600" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'border-l-red-500';
      case 'medium':
        return 'border-l-yellow-500';
      case 'low':
        return 'border-l-green-500';
      default:
        return 'border-l-gray-500';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'confusion':
        return 'bg-yellow-50 border-yellow-200';
      case 'blocker':
        return 'bg-red-50 border-red-200';
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'suggestion':
        return 'bg-blue-50 border-blue-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="flex h-full bg-[#FAFAFA]">
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-[#E3E3E3] bg-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-[#1A1A1A] mb-2">UX Test Results</h2>
              <p className="text-[#555]">Actionable insights from your agent swarm test</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="text-sm text-[#555]">
                <TrendingUp className="w-4 h-4 inline mr-1" />
                {mockInsights.length} insights found
              </div>
            </div>
          </div>
        </div>

        {/* Question Summary */}
        <div className="p-6 bg-white border-b border-[#E3E3E3]">
          <div className="bg-[#F3F3F5] rounded-xl p-4">
            <h3 className="text-[#1A1A1A] mb-2">Answer to your UX question</h3>
            <p className="text-[#555] mb-3">"{testConfig?.question || 'Where do users get confused during checkout?'}"</p>
            <p className="text-[#1A1A1A]">
              Users primarily struggled with <strong>checkout button visibility</strong> and <strong>error message clarity</strong>. 
              The cart review process worked well, suggesting your current design patterns are effective for content organization.
            </p>
          </div>
        </div>

        {/* Insights */}
        <ScrollArea className="flex-1 p-6">
          <div className="space-y-4">
            {mockInsights.map((insight, index) => (
              <motion.div
                key={insight.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className={`border-l-4 ${getSeverityColor(insight.severity)} ${getTypeColor(insight.type)} hover:shadow-md transition-shadow`}>
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        {getInsightIcon(insight.type)}
                        <div className="flex-1">
                          <CardTitle className="text-[#1A1A1A] mb-2">{insight.title}</CardTitle>
                          <p className="text-[#555] text-sm">{insight.description}</p>
                        </div>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {insight.severity} priority
                      </Badge>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="pt-0">
                    {/* Personas */}
                    <div className="mb-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Users className="w-4 h-4 text-[#555]" />
                        <span className="text-sm text-[#555]">Affected personas:</span>
                      </div>
                      <div className="flex gap-2">
                        {insight.personas.map((persona, idx) => (
                          <Badge key={idx} className={`${insight.personaColors[idx]} border-none text-xs`}>
                            {persona}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Suggestions */}
                    <div className="mb-4">
                      <div className="text-sm text-[#555] mb-2">Recommended actions:</div>
                      <ul className="space-y-1">
                        {insight.suggestions.map((suggestion, idx) => (
                          <li key={idx} className="text-sm text-[#1A1A1A] flex items-start gap-2">
                            <div className="w-1.5 h-1.5 bg-[#4F46E5] rounded-full mt-2 flex-shrink-0" />
                            {suggestion}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                      {insight.transcriptMoment && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => onJumpToTranscript(insight.transcriptMoment!)}
                          className="border-[#E3E3E3] text-[#555] hover:bg-[#F3F3F5]"
                        >
                          <ExternalLink className="w-4 h-4 mr-1" />
                          View in Transcript
                        </Button>
                      )}
                      <Button
                        size="sm"
                        onClick={() => onGenerateTicket(insight)}
                        className="bg-[#4F46E5] hover:bg-[#4338CA] text-white"
                      >
                        <FileText className="w-4 h-4 mr-1" />
                        Create Ticket
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Right Sidebar - Summary Stats */}
      <div className="w-64 bg-white border-l border-[#E3E3E3] p-4">
        <div className="space-y-4">
          <div>
            <h4 className="text-[#1A1A1A] mb-3">Test Summary</h4>
            <div className="space-y-3">
              <div className="p-3 bg-[#F3F3F5] rounded-lg">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-[#555]">Success Rate</span>
                  <span className="text-sm text-green-600">73%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: '73%' }}></div>
                </div>
              </div>

              <div className="p-3 bg-[#F3F3F5] rounded-lg">
                <div className="text-xs text-[#555] mb-1">Avg. Completion Time</div>
                <div className="text-lg text-[#1A1A1A]">2m 34s</div>
              </div>

              <div className="p-3 bg-[#F3F3F5] rounded-lg">
                <div className="text-xs text-[#555] mb-1">Drop-off Points</div>
                <div className="text-lg text-[#1A1A1A]">3</div>
                <div className="text-xs text-[#555]">Checkout, Promo, Payment</div>
              </div>
            </div>
          </div>

          <div>
            <h4 className="text-[#1A1A1A] mb-3">Priority Actions</h4>
            <div className="space-y-2">
              <div className="p-2 bg-red-50 border border-red-200 rounded-lg">
                <div className="text-xs text-red-700">HIGH</div>
                <div className="text-sm text-[#1A1A1A]">2 critical issues</div>
              </div>
              <div className="p-2 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="text-xs text-yellow-700">MEDIUM</div>
                <div className="text-sm text-[#1A1A1A]">1 improvement</div>
              </div>
              <div className="p-2 bg-green-50 border border-green-200 rounded-lg">
                <div className="text-xs text-green-700">SUCCESS</div>
                <div className="text-sm text-[#1A1A1A]">1 pattern to reuse</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}