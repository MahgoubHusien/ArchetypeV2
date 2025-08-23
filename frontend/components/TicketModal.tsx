'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Card, CardContent } from './ui/card';
import { Separator } from './ui/separator';
import { 
  Bug, 
  Lightbulb, 
  AlertTriangle, 
  CheckCircle2, 
  Copy, 
  ExternalLink,
  User,
  Calendar,
  Flag,
  FileText,
  Github,
  Monitor
} from 'lucide-react';

interface TicketModalProps {
  isOpen: boolean;
  onClose: () => void;
  insight: any;
}

interface TicketData {
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  type: 'bug' | 'feature' | 'improvement' | 'task';
  assignee: string;
  labels: string[];
  acceptanceCriteria: string;
  reproduction: string;
}

export function TicketModal({ isOpen, onClose, insight }: TicketModalProps) {
  const [ticketData, setTicketData] = useState<TicketData>({
    title: '',
    description: '',
    priority: 'medium',
    type: 'improvement',
    assignee: '',
    labels: [],
    acceptanceCriteria: '',
    reproduction: ''
  });
  
  const [activeTab, setActiveTab] = useState<'details' | 'preview'>('details');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isCreated, setIsCreated] = useState(false);
  const [ticketUrl, setTicketUrl] = useState('');

  // Initialize ticket data based on insight
  useEffect(() => {
    if (insight) {
      const suggestedTitle = generateTicketTitle(insight);
      const suggestedDescription = generateTicketDescription(insight);
      const suggestedType = getTicketType(insight.type);
      const suggestedPriority = getPriority(insight.severity);
      const suggestedLabels = generateLabels(insight);

      setTicketData({
        title: suggestedTitle,
        description: suggestedDescription,
        priority: suggestedPriority,
        type: suggestedType,
        assignee: '',
        labels: suggestedLabels,
        acceptanceCriteria: generateAcceptanceCriteria(insight),
        reproduction: generateReproduction(insight)
      });
    }
  }, [insight]);

  const generateTicketTitle = (insight: any): string => {
    if (!insight) return '';
    
    const prefixes = {
      issue: 'Fix:',
      improvement: 'Improve:',
      observation: 'Investigate:',
      success: 'Document:'
    };
    
    const prefix = prefixes[insight.type] || 'Task:';
    return `${prefix} ${insight.title}`;
  };

  const generateTicketDescription = (insight: any): string => {
    if (!insight) return '';
    
    let description = `## Issue Summary\n${insight.description}\n\n`;
    
    if (insight.evidence) {
      description += `## Evidence\n${insight.evidence}\n\n`;
    }
    
    if (insight.impact) {
      description += `## Impact\n${insight.impact}\n\n`;
    }
    
    if (insight.recommendation) {
      description += `## Recommended Solution\n${insight.recommendation}\n\n`;
    }
    
    description += `## Test Context\n`;
    description += `- **Persona**: ${insight.persona}\n`;
    if (insight.step > 0) {
      description += `- **Step**: ${insight.step}\n`;
    }
    description += `- **Severity**: ${insight.severity}\n`;
    
    return description;
  };

  const getTicketType = (insightType: string): 'bug' | 'feature' | 'improvement' | 'task' => {
    switch (insightType) {
      case 'issue': return 'bug';
      case 'improvement': return 'improvement';
      case 'observation': return 'task';
      case 'success': return 'task';
      default: return 'task';
    }
  };

  const getPriority = (severity: string): 'low' | 'medium' | 'high' | 'urgent' => {
    switch (severity) {
      case 'high': return 'high';
      case 'medium': return 'medium';
      case 'low': return 'low';
      default: return 'medium';
    }
  };

  const generateLabels = (insight: any): string[] => {
    const labels: string[] = ['ux-testing'];
    
    if (insight.persona && insight.persona !== 'Overall') {
      labels.push(`persona-${insight.persona.toLowerCase().replace(/\s+/g, '-')}`);
    }
    
    labels.push(`severity-${insight.severity}`);
    labels.push(`type-${insight.type}`);
    
    return labels;
  };

  const generateAcceptanceCriteria = (insight: any): string => {
    if (!insight) return '';
    
    let criteria = `- [ ] Issue identified in UX testing has been addressed\n`;
    
    if (insight.type === 'issue') {
      criteria += `- [ ] Root cause has been identified and fixed\n`;
      criteria += `- [ ] Solution prevents similar issues in the future\n`;
    }
    
    if (insight.type === 'improvement') {
      criteria += `- [ ] Improvement has been implemented\n`;
      criteria += `- [ ] User experience has been enhanced\n`;
    }
    
    criteria += `- [ ] Changes have been tested with the affected persona type\n`;
    criteria += `- [ ] No regression issues introduced\n`;
    
    return criteria;
  };

  const generateReproduction = (insight: any): string => {
    if (!insight) return '';
    
    let steps = `## Steps to Reproduce\n`;
    steps += `1. Access the test environment\n`;
    steps += `2. Assume the persona: ${insight.persona}\n`;
    
    if (insight.step > 0) {
      steps += `3. Navigate to step ${insight.step} of the user flow\n`;
    }
    
    if (insight.interactions && insight.interactions.length > 0) {
      steps += `4. Perform the following interactions:\n`;
      insight.interactions.forEach((interaction: any, index: number) => {
        steps += `   - ${interaction.action_type || 'Action'}: ${interaction.selector || interaction.result}\n`;
      });
    }
    
    steps += `\n## Expected Result\nUser should be able to complete the task without issues.\n`;
    steps += `\n## Actual Result\n${insight.description}`;
    
    return steps;
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      // Simulate ticket creation API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock ticket URL
      const mockTicketId = Math.floor(Math.random() * 1000) + 1;
      setTicketUrl(`https://github.com/yourproject/issues/${mockTicketId}`);
      setIsCreated(true);
      
    } catch (error) {
      console.error('Failed to create ticket:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setIsCreated(false);
    setTicketUrl('');
    setActiveTab('details');
    onClose();
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-100 text-red-700 border-red-300';
      case 'high': return 'bg-orange-100 text-orange-700 border-orange-300';
      case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-300';
      case 'low': return 'bg-green-100 text-green-700 border-green-300';
      default: return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'bug': return <Bug className="w-4 h-4" />;
      case 'feature': return <Lightbulb className="w-4 h-4" />;
      case 'improvement': return <CheckCircle2 className="w-4 h-4" />;
      case 'task': return <FileText className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  if (isCreated) {
    return (
      <Dialog open={isOpen} onOpenChange={handleClose}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
              Ticket Created Successfully
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle2 className="w-8 h-8 text-green-600" />
              </div>
              <p className="text-gray-600 mb-4">
                Your ticket has been created and is ready for the development team.
              </p>
              
              {ticketUrl && (
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex items-center gap-2 text-sm">
                        <Github className="w-4 h-4" />
                        <span className="font-mono text-gray-600">#{ticketUrl.split('/').pop()}</span>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => copyToClipboard(ticketUrl)}
                        >
                          <Copy className="w-3 h-3 mr-1" />
                          Copy
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => window.open(ticketUrl, '_blank')}
                        >
                          <ExternalLink className="w-3 h-3 mr-1" />
                          View
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
          
          <div className="flex justify-center">
            <Button onClick={handleClose}>Done</Button>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Create Development Ticket
          </DialogTitle>
        </DialogHeader>
        
        {/* Tabs */}
        <div className="flex gap-1 bg-gray-100 p-1 rounded-lg mb-6">
          <Button
            variant={activeTab === 'details' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setActiveTab('details')}
            className="flex-1"
          >
            <Monitor className="w-4 h-4 mr-2" />
            Details
          </Button>
          <Button
            variant={activeTab === 'preview' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setActiveTab('preview')}
            className="flex-1"
          >
            <FileText className="w-4 h-4 mr-2" />
            Preview
          </Button>
        </div>

        {activeTab === 'details' && (
          <div className="space-y-6">
            {/* Insight Summary */}
            {insight && (
              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0">
                      {insight.type === 'issue' && <AlertTriangle className="w-5 h-5 text-red-600" />}
                      {insight.type === 'improvement' && <Lightbulb className="w-5 h-5 text-blue-600" />}
                      {insight.type === 'success' && <CheckCircle2 className="w-5 h-5 text-green-600" />}
                      {insight.type === 'observation' && <Monitor className="w-5 h-5 text-purple-600" />}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 mb-1">{insight.title}</h4>
                      <p className="text-sm text-gray-600 mb-2">{insight.description}</p>
                      <div className="flex gap-2">
                        <Badge className={`${insight.personaColor} border`}>
                          <User className="w-3 h-3 mr-1" />
                          {insight.persona}
                        </Badge>
                        <Badge className={`${getPriorityColor(insight.severity)} border`}>
                          <Flag className="w-3 h-3 mr-1" />
                          {insight.severity}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Ticket Form */}
            <div className="grid grid-cols-2 gap-6">
              {/* Left Column */}
              <div className="space-y-4">
                <div>
                  <Label htmlFor="title">Ticket Title *</Label>
                  <Input
                    id="title"
                    value={ticketData.title}
                    onChange={(e) => setTicketData(prev => ({ ...prev, title: e.target.value }))}
                    className="mt-2"
                    placeholder="Brief description of the issue or task"
                  />
                </div>

                <div>
                  <Label htmlFor="type">Type</Label>
                  <Select value={ticketData.type} onValueChange={(value: any) => setTicketData(prev => ({ ...prev, type: value }))}>
                    <SelectTrigger className="mt-2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="bug">
                        <div className="flex items-center gap-2">
                          <Bug className="w-4 h-4" />
                          Bug Fix
                        </div>
                      </SelectItem>
                      <SelectItem value="improvement">
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4" />
                          Improvement
                        </div>
                      </SelectItem>
                      <SelectItem value="feature">
                        <div className="flex items-center gap-2">
                          <Lightbulb className="w-4 h-4" />
                          New Feature
                        </div>
                      </SelectItem>
                      <SelectItem value="task">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4" />
                          Task
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="priority">Priority</Label>
                  <Select value={ticketData.priority} onValueChange={(value: any) => setTicketData(prev => ({ ...prev, priority: value }))}>
                    <SelectTrigger className="mt-2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="urgent">🔴 Urgent</SelectItem>
                      <SelectItem value="high">🟠 High</SelectItem>
                      <SelectItem value="medium">🟡 Medium</SelectItem>
                      <SelectItem value="low">🟢 Low</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="assignee">Assignee (Optional)</Label>
                  <Input
                    id="assignee"
                    value={ticketData.assignee}
                    onChange={(e) => setTicketData(prev => ({ ...prev, assignee: e.target.value }))}
                    className="mt-2"
                    placeholder="@username or team"
                  />
                </div>
              </div>

              {/* Right Column */}
              <div className="space-y-4">
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={ticketData.description}
                    onChange={(e) => setTicketData(prev => ({ ...prev, description: e.target.value }))}
                    className="mt-2 min-h-[120px]"
                    placeholder="Detailed description of the issue..."
                  />
                </div>

                <div>
                  <Label htmlFor="acceptance">Acceptance Criteria</Label>
                  <Textarea
                    id="acceptance"
                    value={ticketData.acceptanceCriteria}
                    onChange={(e) => setTicketData(prev => ({ ...prev, acceptanceCriteria: e.target.value }))}
                    className="mt-2 min-h-[80px]"
                    placeholder="Define when this ticket is complete..."
                  />
                </div>
              </div>
            </div>

            {ticketData.type === 'bug' && (
              <div>
                <Label htmlFor="reproduction">Reproduction Steps</Label>
                <Textarea
                  id="reproduction"
                  value={ticketData.reproduction}
                  onChange={(e) => setTicketData(prev => ({ ...prev, reproduction: e.target.value }))}
                  className="mt-2 min-h-[100px]"
                  placeholder="Steps to reproduce the issue..."
                />
              </div>
            )}
          </div>
        )}

        {activeTab === 'preview' && (
          <div className="space-y-4">
            <Card>
              <CardContent className="p-6 space-y-4">
                <div className="flex items-center gap-3">
                  {getTypeIcon(ticketData.type)}
                  <h3 className="text-lg font-semibold">{ticketData.title}</h3>
                  <Badge className={`${getPriorityColor(ticketData.priority)} border`}>
                    {ticketData.priority}
                  </Badge>
                </div>
                
                <Separator />
                
                <div className="prose prose-sm max-w-none">
                  <div dangerouslySetInnerHTML={{ 
                    __html: ticketData.description.replace(/\n/g, '<br>') 
                  }} />
                </div>
                
                {ticketData.acceptanceCriteria && (
                  <>
                    <Separator />
                    <div>
                      <h4 className="font-medium mb-2">Acceptance Criteria</h4>
                      <div className="prose prose-sm max-w-none">
                        <div dangerouslySetInnerHTML={{ 
                          __html: ticketData.acceptanceCriteria.replace(/\n/g, '<br>') 
                        }} />
                      </div>
                    </div>
                  </>
                )}
                
                {ticketData.reproduction && (
                  <>
                    <Separator />
                    <div>
                      <h4 className="font-medium mb-2">Reproduction Steps</h4>
                      <div className="prose prose-sm max-w-none">
                        <div dangerouslySetInnerHTML={{ 
                          __html: ticketData.reproduction.replace(/\n/g, '<br>') 
                        }} />
                      </div>
                    </div>
                  </>
                )}
                
                <Separator />
                
                <div className="flex gap-2 flex-wrap">
                  {ticketData.labels.map((label, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {label}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between pt-6 border-t">
          <Button variant="outline" onClick={handleClose}>
            Cancel
          </Button>
          <div className="flex gap-3">
            <Button
              onClick={handleSubmit}
              disabled={isSubmitting || !ticketData.title.trim()}
              className="min-w-[120px]"
            >
              {isSubmitting ? (
                <>Creating...</>
              ) : (
                <>
                  <Github className="w-4 h-4 mr-2" />
                  Create Ticket
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}