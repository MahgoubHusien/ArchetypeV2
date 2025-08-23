'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Plus, X, User, Sparkles } from 'lucide-react';

interface TestConfig {
  question: string;
  url: string;
  selector: string;
  personas: Array<{
    id: string;
    name: string;
    age: string;
    context: string;
    color: string;
  }>;
}

interface TestSetupProps {
  isOpen: boolean;
  onClose: () => void;
  onRunTest: (config: TestConfig) => void;
}

const PRESET_PERSONAS = [
  { id: '1', name: 'Tech-Savvy Millennial', age: '28', context: 'Frequent online shopper, uses mobile primarily', color: 'bg-blue-100 text-blue-700' },
  { id: '2', name: 'Senior User', age: '65', context: 'Less familiar with technology, needs clear instructions', color: 'bg-purple-100 text-purple-700' },
  { id: '3', name: 'Busy Parent', age: '35', context: 'Time-constrained, shopping for family needs', color: 'bg-green-100 text-green-700' },
  { id: '4', name: 'Budget Conscious Student', age: '22', context: 'Price-sensitive, looks for deals and discounts', color: 'bg-orange-100 text-orange-700' },
  { id: '5', name: 'Power User', age: '30', context: 'Tech expert, expects advanced features and shortcuts', color: 'bg-red-100 text-red-700' },
];

const COLORS = [
  'bg-blue-100 text-blue-700',
  'bg-green-100 text-green-700',
  'bg-purple-100 text-purple-700',
  'bg-orange-100 text-orange-700',
  'bg-pink-100 text-pink-700',
  'bg-yellow-100 text-yellow-700',
  'bg-indigo-100 text-indigo-700',
];

export function TestSetup({ isOpen, onClose, onRunTest }: TestSetupProps) {
  const [url, setUrl] = useState('');
  const [question, setQuestion] = useState('');
  const [selector, setSelector] = useState('');
  const [selectedPersonas, setSelectedPersonas] = useState<typeof PRESET_PERSONAS>([]);
  const [customPersonaName, setCustomPersonaName] = useState('');
  const [customPersonaAge, setCustomPersonaAge] = useState('');
  const [customPersonaContext, setCustomPersonaContext] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!url) {
      newErrors.url = 'URL is required';
    } else if (!url.startsWith('http://') && !url.startsWith('https://')) {
      newErrors.url = 'URL must start with http:// or https://';
    }
    
    if (!question) {
      newErrors.question = 'UX question is required';
    }
    
    if (selectedPersonas.length === 0) {
      newErrors.personas = 'At least one persona is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (validateForm()) {
      try {
        await onRunTest({
          url,
          question,
          selector,
          personas: selectedPersonas,
        });
        resetForm();
      } catch (error) {
        // Error is handled in parent component
        console.error('Test submission error:', error);
      }
    }
  };

  const resetForm = () => {
    setUrl('');
    setQuestion('');
    setSelector('');
    setSelectedPersonas([]);
    setCustomPersonaName('');
    setCustomPersonaAge('');
    setCustomPersonaContext('');
    setErrors({});
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const togglePersona = (persona: typeof PRESET_PERSONAS[0]) => {
    setErrors({ ...errors, personas: '' });
    const exists = selectedPersonas.find(p => p.id === persona.id);
    if (exists) {
      setSelectedPersonas(selectedPersonas.filter(p => p.id !== persona.id));
    } else {
      setSelectedPersonas([...selectedPersonas, persona]);
    }
  };

  const addCustomPersona = () => {
    if (customPersonaName && customPersonaAge && customPersonaContext) {
      const newPersona = {
        id: Date.now().toString(),
        name: customPersonaName,
        age: customPersonaAge,
        context: customPersonaContext,
        color: COLORS[selectedPersonas.length % COLORS.length],
      };
      setSelectedPersonas([...selectedPersonas, newPersona]);
      setCustomPersonaName('');
      setCustomPersonaAge('');
      setCustomPersonaContext('');
      setErrors({ ...errors, personas: '' });
    }
  };

  const removePersona = (id: string) => {
    setSelectedPersonas(selectedPersonas.filter(p => p.id !== id));
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] bg-white border-gray-200 shadow-2xl">
        <DialogHeader className="border-b pb-4">
          <DialogTitle className="text-2xl font-bold text-gray-900">Create New UX Test</DialogTitle>
          <DialogDescription className="text-gray-600">
            Configure your test parameters and select personas to simulate user interactions
          </DialogDescription>
        </DialogHeader>
        
        <ScrollArea className="h-[calc(90vh-200px)] pr-4">
          <div className="space-y-6 py-4">
            {/* URL Input */}
            <div className="space-y-2">
              <Label htmlFor="url" className="text-sm font-semibold text-gray-700">
                Website URL <span className="text-red-500">*</span>
              </Label>
              <Input
                id="url"
                type="url"
                placeholder="https://example.com"
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value);
                  setErrors({ ...errors, url: '' });
                }}
                className={`bg-white border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-colors select-text ${errors.url ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''}`}
                style={{ userSelect: 'text', WebkitUserSelect: 'text' }}
                autoComplete="off"
                spellCheck={false}
              />
              {errors.url && <p className="text-sm text-red-500">{errors.url}</p>}
            </div>

            {/* Question Input */}
            <div className="space-y-2">
              <Label htmlFor="question" className="text-sm font-semibold text-gray-700">
                UX Question <span className="text-red-500">*</span>
              </Label>
              <Textarea
                id="question"
                placeholder="What specific user experience aspect would you like to test?"
                value={question}
                onChange={(e) => {
                  setQuestion(e.target.value);
                  setErrors({ ...errors, question: '' });
                }}
                className={`bg-gray-50 border-gray-300 focus:border-blue-500 focus:ring-blue-500 min-h-[80px] ${errors.question ? 'border-red-500' : ''}`}
              />
              {errors.question && <p className="text-sm text-red-500">{errors.question}</p>}
            </div>

            {/* CSS Selector (Optional) */}
            <div className="space-y-2">
              <Label htmlFor="selector" className="text-sm font-semibold text-gray-700">
                Starting Element CSS Selector (Optional)
              </Label>
              <Input
                id="selector"
                placeholder="#checkout-button or .nav-menu"
                value={selector}
                onChange={(e) => setSelector(e.target.value)}
                className="bg-gray-50 border-gray-300 focus:border-blue-500 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500">Specify a CSS selector to focus the test on a specific element</p>
            </div>

            {/* Persona Selection */}
            <div className="space-y-3">
              <Label className="text-sm font-semibold text-gray-700">
                Select Personas <span className="text-red-500">*</span>
              </Label>
              {errors.personas && <p className="text-sm text-red-500">{errors.personas}</p>}
              
              {/* Selected Personas */}
              {selectedPersonas.length > 0 && (
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <p className="text-sm font-medium text-blue-900 mb-2">Selected Personas ({selectedPersonas.length})</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedPersonas.map((persona) => (
                      <Badge
                        key={persona.id}
                        className={`${persona.color} border-none px-3 py-1.5 flex items-center gap-2`}
                      >
                        <User className="w-3 h-3" />
                        {persona.name} ({persona.age})
                        <button
                          onClick={() => removePersona(persona.id)}
                          className="ml-1 hover:opacity-70"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Preset Personas */}
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <p className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  Preset Personas
                </p>
                <div className="grid grid-cols-1 gap-3">
                  {PRESET_PERSONAS.map((persona) => {
                    const isSelected = selectedPersonas.find(p => p.id === persona.id);
                    return (
                      <div
                        key={persona.id}
                        onClick={() => togglePersona(persona)}
                        className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                          isSelected 
                            ? 'border-blue-500 bg-blue-50' 
                            : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">{persona.name}</p>
                            <p className="text-sm text-gray-600">Age: {persona.age}</p>
                            <p className="text-sm text-gray-500 mt-1">{persona.context}</p>
                          </div>
                          <div className={`w-5 h-5 rounded-full border-2 ${
                            isSelected ? 'bg-blue-500 border-blue-500' : 'border-gray-300'
                          }`}>
                            {isSelected && (
                              <svg className="w-full h-full text-white" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Custom Persona */}
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <p className="text-sm font-medium text-gray-700 mb-3">Add Custom Persona</p>
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <Input
                      placeholder="Name"
                      value={customPersonaName}
                      onChange={(e) => setCustomPersonaName(e.target.value)}
                      className="bg-white"
                    />
                    <Input
                      placeholder="Age"
                      type="number"
                      value={customPersonaAge}
                      onChange={(e) => setCustomPersonaAge(e.target.value)}
                      className="bg-white"
                    />
                  </div>
                  <Textarea
                    placeholder="Context/Description - Describe the persona's background, goals, and behaviors"
                    value={customPersonaContext}
                    onChange={(e) => setCustomPersonaContext(e.target.value)}
                    className="bg-white min-h-[80px]"
                  />
                </div>
                <Button
                  onClick={addCustomPersona}
                  disabled={!customPersonaName || !customPersonaAge || !customPersonaContext}
                  className="mt-3 bg-gray-700 hover:bg-gray-800 text-white"
                  size="sm"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Custom Persona
                </Button>
              </div>
            </div>
          </div>
        </ScrollArea>

        {/* Footer Actions */}
        <div className="border-t pt-4 flex justify-between items-center bg-white">
          <Button
            onClick={handleClose}
            variant="outline"
            className="border-gray-300 text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </Button>
          <div className="flex gap-3">
            <Button
              onClick={handleSubmit}
              className="bg-[#4F46E5] hover:bg-[#4338CA] text-white px-6"
            >
              <Sparkles className="w-4 h-4 mr-2" />
              Run Test with {selectedPersonas.length} Persona{selectedPersonas.length !== 1 ? 's' : ''}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}