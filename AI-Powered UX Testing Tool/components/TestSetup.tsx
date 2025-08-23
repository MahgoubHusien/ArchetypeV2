import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { X, Plus, Globe, Target, Users, Play } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface Persona {
  id: string;
  name: string;
  age: string;
  context: string;
  color: string;
}

interface TestSetupProps {
  isOpen: boolean;
  onClose: () => void;
  onRunTest: (testConfig: any) => void;
}

export function TestSetup({ isOpen, onClose, onRunTest }: TestSetupProps) {
  const [question, setQuestion] = useState('');
  const [url, setUrl] = useState('');
  const [selector, setSelector] = useState('');
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [newPersona, setNewPersona] = useState({ name: '', age: '', context: '' });

  const personaColors = [
    'bg-pink-100 text-pink-700',
    'bg-blue-100 text-blue-700',
    'bg-green-100 text-green-700',
    'bg-purple-100 text-purple-700',
    'bg-orange-100 text-orange-700',
    'bg-indigo-100 text-indigo-700'
  ];

  const addPersona = () => {
    if (newPersona.name && newPersona.age) {
      const persona: Persona = {
        id: Date.now().toString(),
        name: newPersona.name,
        age: newPersona.age,
        context: newPersona.context,
        color: personaColors[personas.length % personaColors.length]
      };
      setPersonas([...personas, persona]);
      setNewPersona({ name: '', age: '', context: '' });
    }
  };

  const removePersona = (id: string) => {
    setPersonas(personas.filter(p => p.id !== id));
  };

  const handleRunTest = () => {
    const testConfig = {
      question,
      url,
      selector,
      personas
    };
    onRunTest(testConfig);
  };

  const isValidConfig = question && url && personas.length > 0;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-white">
        <DialogHeader>
          <DialogTitle className="text-[#1A1A1A] flex items-center gap-2">
            <Target className="w-5 h-5" />
            New UX Test
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* UX Question */}
          <div className="space-y-2">
            <label className="text-[#1A1A1A] flex items-center gap-2">
              <span>What UX question do you want to answer?</span>
            </label>
            <Textarea
              placeholder="e.g., Where do users get confused during our checkout flow?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="bg-[#F3F3F5] border-[#E3E3E3] focus:border-[#4F46E5] min-h-20"
            />
          </div>

          {/* URL */}
          <div className="space-y-2">
            <label className="text-[#1A1A1A] flex items-center gap-2">
              <Globe className="w-4 h-4" />
              Where should agents begin?
            </label>
            <Input
              placeholder="https://example.com/checkout"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="bg-[#F3F3F5] border-[#E3E3E3] focus:border-[#4F46E5]"
            />
          </div>

          {/* CSS Selector (Optional) */}
          <div className="space-y-2">
            <label className="text-[#555] flex items-center gap-2">
              <Target className="w-4 h-4" />
              CSS Selector (Optional)
            </label>
            <Input
              placeholder=".checkout-button, #payment-form"
              value={selector}
              onChange={(e) => setSelector(e.target.value)}
              className="bg-[#F3F3F5] border-[#E3E3E3] focus:border-[#4F46E5]"
            />
            <p className="text-xs text-[#555]">Specify which element or feature to focus on</p>
          </div>

          {/* Persona Builder */}
          <div className="space-y-4">
            <label className="text-[#1A1A1A] flex items-center gap-2">
              <Users className="w-4 h-4" />
              Test Personas
            </label>
            
            {/* Existing Personas */}
            <AnimatePresence>
              {personas.map((persona) => (
                <motion.div
                  key={persona.id}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="bg-[#F3F3F5] rounded-xl p-4 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <Badge className={`${persona.color} border-none`}>
                      {persona.name}, {persona.age}
                    </Badge>
                    <button
                      onClick={() => removePersona(persona.id)}
                      className="text-[#555] hover:text-red-500 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  {persona.context && (
                    <p className="text-sm text-[#555]">"{persona.context}"</p>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Add New Persona */}
            <div className="bg-[#F3F3F5] rounded-xl p-4 space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <Input
                  placeholder="e.g., Etsy mom"
                  value={newPersona.name}
                  onChange={(e) => setNewPersona({ ...newPersona, name: e.target.value })}
                  className="bg-white border-[#E3E3E3]"
                />
                <Input
                  placeholder="Age (e.g., 38)"
                  value={newPersona.age}
                  onChange={(e) => setNewPersona({ ...newPersona, age: e.target.value })}
                  className="bg-white border-[#E3E3E3]"
                />
              </div>
              <Textarea
                placeholder="Context (optional): Clicked Instagram ad → looking for gift for daughter"
                value={newPersona.context}
                onChange={(e) => setNewPersona({ ...newPersona, context: e.target.value })}
                className="bg-white border-[#E3E3E3] min-h-16"
              />
              <Button
                onClick={addPersona}
                disabled={!newPersona.name || !newPersona.age}
                className="bg-[#E9EBEF] text-[#1A1A1A] hover:bg-[#CBCED4] border-none"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Persona
              </Button>
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
            onClick={handleRunTest}
            disabled={!isValidConfig}
            className="flex-1 bg-[#4F46E5] hover:bg-[#4338CA] text-white"
          >
            <Play className="w-4 h-4 mr-2" />
            Run Swarm Test
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}