import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { X, FileText, ExternalLink, Copy, Check } from 'lucide-react';
import { motion } from 'motion/react';

interface TicketModalProps {
  isOpen: boolean;
  onClose: () => void;
  insight?: {
    title: string;
    description: string;
    severity: string;
    personas: string[];
    personaColors: string[];
    suggestions: string[];
  };
}

export function TicketModal({ isOpen, onClose, insight }: TicketModalProps) {
  const [title, setTitle] = useState(insight?.title || '');
  const [description, setDescription] = useState('');
  const [steps, setSteps] = useState('');
  const [platform, setPlatform] = useState('jira');
  const [priority, setPriority] = useState(insight?.severity || 'medium');
  const [copied, setCopied] = useState(false);

  useState(() => {
    if (insight) {
      setTitle(insight.title);
      const stepsText = insight.suggestions.map((s, i) => `${i + 1}. ${s}`).join('\n');
      setSteps(stepsText);
      setDescription(`${insight.description}\n\nAffected personas: ${insight.personas.join(', ')}`);
    }
  }, [insight]);

  const handleCopy = () => {
    const ticketContent = `
Title: ${title}

Description:
${description}

Steps to Reproduce/Fix:
${steps}

Priority: ${priority}
Affected Personas: ${insight?.personas.join(', ') || 'N/A'}
    `.trim();

    navigator.clipboard.writeText(ticketContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExport = () => {
    // Simulate export to different platforms
    console.log('Exporting to:', platform);
    onClose();
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'jira':
        return '🔷';
      case 'linear':
        return '📐';
      case 'notion':
        return '📝';
      case 'slack':
        return '💬';
      default:
        return '📋';
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-white">
        <DialogHeader>
          <DialogTitle className="text-[#1A1A1A] flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Create Ticket
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Platform Selection */}
          <div className="space-y-2">
            <label className="text-[#1A1A1A]">Export to</label>
            <Select value={platform} onValueChange={setPlatform}>
              <SelectTrigger className="bg-[#F3F3F5] border-[#E3E3E3]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="jira">🔷 Jira</SelectItem>
                <SelectItem value="linear">📐 Linear</SelectItem>
                <SelectItem value="notion">📝 Notion</SelectItem>
                <SelectItem value="slack">💬 Slack</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Title */}
          <div className="space-y-2">
            <label className="text-[#1A1A1A]">Title</label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="bg-[#F3F3F5] border-[#E3E3E3] focus:border-[#4F46E5]"
              placeholder="Brief description of the issue"
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <label className="text-[#1A1A1A]">Description</label>
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="bg-[#F3F3F5] border-[#E3E3E3] focus:border-[#4F46E5] min-h-24"
              placeholder="Detailed description of the issue and its impact"
            />
          </div>

          {/* Steps/Actions */}
          <div className="space-y-2">
            <label className="text-[#1A1A1A]">Steps to Reproduce / Recommended Actions</label>
            <Textarea
              value={steps}
              onChange={(e) => setSteps(e.target.value)}
              className="bg-[#F3F3F5] border-[#E3E3E3] focus:border-[#4F46E5] min-h-32"
              placeholder="1. Step one&#10;2. Step two&#10;3. Step three"
            />
          </div>

          {/* Priority */}
          <div className="space-y-2">
            <label className="text-[#1A1A1A]">Priority</label>
            <Select value={priority} onValueChange={setPriority}>
              <SelectTrigger className="bg-[#F3F3F5] border-[#E3E3E3]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="high">🔴 High</SelectItem>
                <SelectItem value="medium">🟡 Medium</SelectItem>
                <SelectItem value="low">🟢 Low</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Personas */}
          {insight?.personas && (
            <div className="space-y-2">
              <label className="text-[#1A1A1A]">Affected Personas</label>
              <div className="flex gap-2">
                {insight.personas.map((persona, idx) => (
                  <Badge key={idx} className={`${insight.personaColors[idx]} border-none text-xs`}>
                    {persona}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Screenshot Placeholder */}
          <div className="space-y-2">
            <label className="text-[#1A1A1A]">Screenshot</label>
            <div className="border-2 border-dashed border-[#E3E3E3] rounded-xl p-8 text-center bg-[#F9F9F9]">
              <div className="text-[#555] mb-2">Screenshot will be attached automatically</div>
              <div className="text-xs text-[#555]">From agent interaction at timestamp {insight ? '14:32:15' : 'N/A'}</div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4 border-t border-[#E3E3E3]">
          <Button
            onClick={onClose}
            variant="outline"
            className="flex-1 border-[#E3E3E3] text-[#555] hover:bg-[#F3F3F5]"
          >
            Cancel
          </Button>
          <Button
            onClick={handleCopy}
            variant="outline"
            className="border-[#E3E3E3] text-[#555] hover:bg-[#F3F3F5]"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 mr-2" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="w-4 h-4 mr-2" />
                Copy
              </>
            )}
          </Button>
          <Button
            onClick={handleExport}
            className="flex-1 bg-[#4F46E5] hover:bg-[#4338CA] text-white"
          >
            <span className="mr-2">{getPlatformIcon(platform)}</span>
            Export to {platform.charAt(0).toUpperCase() + platform.slice(1)}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}