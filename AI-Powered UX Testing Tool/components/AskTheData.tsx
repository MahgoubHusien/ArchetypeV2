import { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Send, Bookmark, Copy, FileText, MessageCircle, TrendingDown, Users, Clock } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  hasActions?: boolean;
  data?: {
    type: 'table' | 'chart' | 'insight';
    content: any;
  };
}

const sampleQuestions = [
  "Where did most moms drop off?",
  "What confused users about 'Edit with AI'?",
  "Which personas completed successfully?",
  "What was the average time to checkout?"
];

const mockMessages: ChatMessage[] = [
  {
    id: '1',
    type: 'assistant',
    content: 'Hi! I can help you analyze your UX test data. Ask me anything about user behaviors, drop-off points, or persona performance.',
    timestamp: '14:35:01',
    hasActions: false
  }
];

interface AskTheDataProps {
  testConfig: any;
}

export function AskTheData({ testConfig }: AskTheDataProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(mockMessages);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
      })
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: generateMockResponse(message),
        timestamp: new Date().toLocaleTimeString('en-US', { 
          hour12: false, 
          hour: '2-digit', 
          minute: '2-digit', 
          second: '2-digit' 
        }),
        hasActions: true,
        data: generateMockData(message)
      };

      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1500);
  };

  const generateMockResponse = (question: string) => {
    const lowerQ = question.toLowerCase();
    
    if (lowerQ.includes('drop off') || lowerQ.includes('abandoned')) {
      return "Based on the test data, **67% of Etsy moms dropped off** at the checkout button step. The main issue was button visibility - users spent an average of 28 seconds searching for the checkout button before giving up.";
    }
    
    if (lowerQ.includes('confused') || lowerQ.includes('edit with ai')) {
      return "Users were primarily confused by **unclear error messaging** when promo codes failed validation. The error message 'Invalid code' didn't explain what was wrong or how to fix it.";
    }
    
    if (lowerQ.includes('persona') || lowerQ.includes('completed')) {
      return "**SaaS PMs had the highest completion rate** at 85%, followed by Busy Professionals at 78%. Etsy moms had the lowest at 45% due to checkout button visibility issues.";
    }
    
    if (lowerQ.includes('time') || lowerQ.includes('average')) {
      return "The average time to complete checkout was **2 minutes 34 seconds**. Successful users averaged 1m 45s, while users who encountered issues took up to 4m 12s.";
    }
    
    return "I found several interesting patterns in your test data. The main pain points were button visibility and error message clarity. Would you like me to dive deeper into any specific aspect?";
  };

  const generateMockData = (question: string) => {
    const lowerQ = question.toLowerCase();
    
    if (lowerQ.includes('drop off')) {
      return {
        type: 'table',
        content: {
          headers: ['Persona', 'Started', 'Completed', 'Drop-off Rate'],
          rows: [
            ['Etsy mom', '6', '2', '67%'],
            ['SaaS PM', '4', '3', '25%'],
            ['Busy professional', '3', '2', '33%']
          ]
        }
      };
    }
    
    if (lowerQ.includes('time')) {
      return {
        type: 'insight',
        content: {
          metric: '2m 34s',
          change: '+23s vs baseline',
          breakdown: 'Page load: 12s, Navigation: 45s, Form fill: 97s'
        }
      };
    }
    
    return null;
  };

  const handleSampleQuestion = (question: string) => {
    setInput(question);
  };

  const handleBookmark = (messageId: string) => {
    // Implement bookmark functionality
    console.log('Bookmark message:', messageId);
  };

  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const handleMakeTicket = (content: string) => {
    // Implement ticket creation
    console.log('Make ticket for:', content);
  };

  return (
    <div className="flex flex-col h-full bg-[#FAFAFA]">
      {/* Header */}
      <div className="p-6 border-b border-[#E3E3E3] bg-white">
        <div className="flex items-center gap-2 mb-2">
          <MessageCircle className="w-5 h-5 text-[#4F46E5]" />
          <h2 className="text-[#1A1A1A]">Ask the Data</h2>
        </div>
        <p className="text-[#555]">Chat with your UX test results to discover deeper insights</p>
      </div>

      {/* Sample Questions */}
      {messages.length <= 1 && (
        <div className="p-6 bg-white border-b border-[#E3E3E3]">
          <div className="mb-3">
            <h3 className="text-[#1A1A1A] mb-2">Try asking:</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {sampleQuestions.map((question, idx) => (
              <Button
                key={idx}
                onClick={() => handleSampleQuestion(question)}
                variant="outline"
                size="sm"
                className="border-[#E3E3E3] text-[#555] hover:bg-[#F3F3F5] hover:border-[#4F46E5] hover:text-[#4F46E5]"
              >
                "{question}"
              </Button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <ScrollArea className="flex-1 p-6" ref={scrollRef}>
        <div className="space-y-4 max-w-4xl">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-2xl ${message.type === 'user' ? 'ml-8' : 'mr-8'}`}>
                  <div
                    className={`rounded-2xl px-4 py-3 ${
                      message.type === 'user'
                        ? 'bg-[#4F46E5] text-white'
                        : 'bg-white border border-[#E3E3E3]'
                    }`}
                  >
                    <div className="prose prose-sm max-w-none">
                      {message.content.split('**').map((part, idx) => 
                        idx % 2 === 1 ? <strong key={idx}>{part}</strong> : part
                      )}
                    </div>
                  </div>

                  {/* Data visualization */}
                  {message.data && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="mt-3 bg-white border border-[#E3E3E3] rounded-xl overflow-hidden"
                    >
                      {message.data.type === 'table' && (
                        <div className="p-4">
                          <table className="w-full text-sm">
                            <thead>
                              <tr className="border-b border-[#E3E3E3]">
                                {message.data.content.headers.map((header: string, idx: number) => (
                                  <th key={idx} className="text-left p-2 text-[#555]">{header}</th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {message.data.content.rows.map((row: string[], idx: number) => (
                                <tr key={idx} className="border-b border-[#E3E3E3] last:border-0">
                                  {row.map((cell, cellIdx) => (
                                    <td key={cellIdx} className="p-2 text-[#1A1A1A]">{cell}</td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}

                      {message.data.type === 'insight' && (
                        <div className="p-4">
                          <div className="flex items-center gap-4">
                            <div className="text-center">
                              <div className="text-2xl text-[#1A1A1A] mb-1">{message.data.content.metric}</div>
                              <div className="text-xs text-[#555]">Average Time</div>
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <TrendingDown className="w-4 h-4 text-red-500" />
                                <span className="text-sm text-red-600">{message.data.content.change}</span>
                              </div>
                              <div className="text-xs text-[#555]">{message.data.content.breakdown}</div>
                            </div>
                          </div>
                        </div>
                      )}
                    </motion.div>
                  )}

                  {/* Actions */}
                  {message.hasActions && message.type === 'assistant' && (
                    <div className="flex gap-2 mt-3">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleBookmark(message.id)}
                        className="border-[#E3E3E3] text-[#555] hover:bg-[#F3F3F5]"
                      >
                        <Bookmark className="w-4 h-4 mr-1" />
                        Bookmark
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleCopy(message.content)}
                        className="border-[#E3E3E3] text-[#555] hover:bg-[#F3F3F5]"
                      >
                        <Copy className="w-4 h-4 mr-1" />
                        Copy
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => handleMakeTicket(message.content)}
                        className="bg-[#4F46E5] hover:bg-[#4338CA] text-white"
                      >
                        <FileText className="w-4 h-4 mr-1" />
                        Make Ticket
                      </Button>
                    </div>
                  )}

                  <div className="text-xs text-[#555] mt-2 text-right">
                    {message.timestamp}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Loading indicator */}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-start"
            >
              <div className="max-w-2xl mr-8">
                <div className="bg-white border border-[#E3E3E3] rounded-2xl px-4 py-3">
                  <div className="flex gap-1">
                    <motion.div
                      className="w-2 h-2 bg-[#555] rounded-full"
                      animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ duration: 1, repeat: Infinity, delay: 0 }}
                    />
                    <motion.div
                      className="w-2 h-2 bg-[#555] rounded-full"
                      animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                    />
                    <motion.div
                      className="w-2 h-2 bg-[#555] rounded-full"
                      animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                    />
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="p-6 border-t border-[#E3E3E3] bg-white">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage(input);
          }}
          className="flex gap-3"
        >
          <Input
            placeholder="Ask a question about this UX session..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 bg-[#F3F3F5] border-[#E3E3E3] focus:border-[#4F46E5]"
            disabled={isLoading}
          />
          <Button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="bg-[#4F46E5] hover:bg-[#4338CA] text-white"
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}