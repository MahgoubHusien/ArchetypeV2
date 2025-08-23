'use client';

import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Search, Plus, Calendar, Users, Loader2, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import { runApi, agentApi, Run, Agent } from '@/lib/api';
import { mockRunApi, mockAgentApi } from '@/lib/mockApi';
import { toast } from 'sonner';

interface UXTest {
  id: string;
  title: string;
  question: string;
  date: string;
  time: string;
  personas: { name: string; color: string }[];
  status: 'completed' | 'running' | 'failed';
  url?: string;
}

interface DashboardProps {
  onNewTest: () => void;
  onSelectTest: (test: UXTest) => void;
}

export function Dashboard({ onNewTest, onSelectTest }: DashboardProps) {
  const [selectedFolder, setSelectedFolder] = useState('all');
  const [tests, setTests] = useState<UXTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [useMockData, setUseMockData] = useState(false);

  useEffect(() => {
    loadTests();
  }, []);

  const loadTests = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Try real API first, fallback to mock if it fails
      let runsResponse;
      let usesMock = false;
      
      try {
        runsResponse = await runApi.getAll();
      } catch (apiError: any) {
        console.warn('Real API failed, using mock data:', apiError.message);
        runsResponse = await mockRunApi.getAll();
        usesMock = true;
        setUseMockData(true);
        
        // Show info toast only once when switching to mock
        if (!useMockData) {
          toast.info('Using mock data', {
            description: 'Backend is not available. Displaying sample data.',
            duration: 3000,
          });
        }
      }
      
      const runs = runsResponse.data;
      
      if (!runs || runs.length === 0) {
        setTests([]);
        setLoading(false);
        return;
      }

      const testList: UXTest[] = [];
      const api = usesMock ? mockAgentApi : agentApi;
      const agentPromises = runs.map(run => api.getByRunId(run.run_id));
      
      const agentResponses = await Promise.all(agentPromises);
      
      runs.forEach((run, index) => {
        const agents = agentResponses[index].data;
        
        const date = new Date(run.created_at);
        const formattedDate = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const formattedTime = date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
        
        const personas = agents.map((agent, idx) => ({
          name: agent.persona || `Agent ${idx + 1}`,
          color: getPersonaColor(idx)
        }));
        
        const allCompleted = agents.every(a => a.status === 'completed');
        const anyFailed = agents.some(a => a.status === 'failed');
        
        testList.push({
          id: run.run_id,
          title: run.ux_question ? `${run.url} Analysis` : 'UX Test',
          question: run.ux_question || 'No question provided',
          date: formattedDate,
          time: formattedTime,
          personas,
          status: anyFailed ? 'failed' : (allCompleted ? 'completed' : 'running'),
          url: run.url
        });
      });
      
      setTests(testList);
    } catch (err: any) {
      console.error('Error loading tests:', err);
      
      // Check if it's a network error (backend not running)
      if (err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
        setError('Backend server is not running. Please start the server on port 8000.');
        toast.error('Cannot connect to backend', {
          description: 'Please ensure the backend server is running on port 8000',
          duration: 5000,
        });
      } else {
        setError('Failed to load tests');
        toast.error('Failed to load tests', {
          description: err.response?.data?.message || err.message || 'An unexpected error occurred',
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const getPersonaColor = (index: number): string => {
    const colors = [
      'bg-pink-100 text-pink-700',
      'bg-blue-100 text-blue-700',
      'bg-green-100 text-green-700',
      'bg-purple-100 text-purple-700',
      'bg-orange-100 text-orange-700',
      'bg-indigo-100 text-indigo-700',
      'bg-gray-100 text-gray-700'
    ];
    return colors[index % colors.length];
  };

  const groupedTests = tests.reduce((acc, test) => {
    if (!acc[test.date]) {
      acc[test.date] = [];
    }
    acc[test.date].push(test);
    return acc;
  }, {} as Record<string, UXTest[]>);

  const folders = [
    { name: 'all', count: tests.length },
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col shadow-sm">
        <div className="p-4 border-b border-gray-200">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input 
              placeholder="Search tests..." 
              className="pl-10 bg-gray-50 border-gray-200 focus:border-[#4F46E5] focus:ring-2 focus:ring-[#4F46E5]/20 transition-all"
            />
          </div>
        </div>

        <div className="flex-1 p-4">
          <div className="mb-6">
            <div className="text-[#555] mb-3">Folders</div>
            <div className="space-y-1">
              {folders.map((folder) => (
                <motion.button
                  key={folder.name}
                  onClick={() => setSelectedFolder(folder.name)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition-all duration-200 ${
                    selectedFolder === folder.name 
                      ? 'bg-[#4F46E5]/10 text-[#4F46E5] font-medium' 
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                  whileHover={{ x: 2 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <span className="capitalize">{folder.name}</span>
                  <span className="text-xs bg-gray-100 px-2 py-0.5 rounded-full">{folder.count}</span>
                </motion.button>
              ))}
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-gray-200">
          <Button 
            onClick={onNewTest}
            className="w-full bg-[#4F46E5] hover:bg-[#4338CA] text-white rounded-xl shadow-md hover:shadow-lg transition-all duration-200"
          >
            <Plus className="w-4 h-4 mr-2" />
            New UX Test
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <div className="p-6 border-b border-gray-200 bg-white">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">UX Tests</h1>
          <p className="text-gray-600">Run AI agents to test user flows and gather insights</p>
        </div>

        <div className="flex-1 p-6 overflow-auto">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="w-8 h-8 animate-spin text-[#4F46E5]" />
            </div>
          ) : error ? (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center h-full max-w-md mx-auto text-center"
            >
              <div className="w-20 h-20 bg-red-50 rounded-full flex items-center justify-center mb-6">
                <div className="text-3xl">⚠️</div>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Connection Error</h2>
              <p className="text-gray-600 mb-6">{error}</p>
              <div className="space-y-3">
                <Button 
                  onClick={loadTests}
                  className="bg-[#4F46E5] hover:bg-[#4338CA] text-white"
                >
                  Retry Connection
                </Button>
                <p className="text-sm text-gray-500">
                  To start the backend, run: <code className="bg-gray-100 px-2 py-1 rounded">cd backend && python main.py</code>
                </p>
              </div>
            </motion.div>
          ) : tests.length === 0 ? (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center h-full max-w-md mx-auto text-center"
            >
              <div className="w-24 h-24 bg-[#4F46E5]/10 rounded-full flex items-center justify-center mb-6">
                <Sparkles className="w-12 h-12 text-[#4F46E5]" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">No tests yet</h2>
              <p className="text-gray-600 mb-8">Create your first UX test to start gathering insights from AI-powered user simulations.</p>
              <Button 
                onClick={onNewTest}
                className="bg-[#4F46E5] hover:bg-[#4338CA] text-white shadow-md hover:shadow-lg transition-all"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Test
              </Button>
            </motion.div>
          ) : (
            <div className="space-y-6">
              {Object.entries(groupedTests).map(([date, dateTests]) => (
                <div key={date}>
                  <div className="text-[#555] mb-4 flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    {date}
                  </div>
                  {dateTests.map((test) => (
                    <motion.div
                      key={test.id}
                      className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm hover:shadow-lg hover:border-[#4F46E5]/30 transition-all duration-200 cursor-pointer mb-4 group"
                      onClick={() => onSelectTest(test)}
                      whileHover={{ y: -2 }}
                      whileTap={{ scale: 0.99 }}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h3 className="text-gray-900 font-semibold mb-1 group-hover:text-[#4F46E5] transition-colors">{test.title}</h3>
                          <p className="text-gray-600 text-sm line-clamp-1">{test.question}</p>
                        </div>
                        <div className="flex items-center gap-2 text-gray-500 text-sm">
                          <div className={`w-2 h-2 rounded-full animate-pulse ${
                            test.status === 'completed' ? 'bg-green-500 animate-none' : 
                            test.status === 'running' ? 'bg-yellow-500' : 
                            'bg-red-500 animate-none'
                          }`}></div>
                          {test.time}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-gray-400" />
                        <div className="flex gap-1.5 flex-wrap">
                          {test.personas.map((persona, idx) => (
                            <Badge key={idx} className={`${persona.color} border-none text-xs px-2 py-0.5`}>
                              {persona.name}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}