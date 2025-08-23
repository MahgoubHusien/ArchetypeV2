'use client';

import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Search, Plus, Calendar, Users, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { runApi, agentApi, Run, Agent } from '@/lib/api';

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

  useEffect(() => {
    loadTests();
  }, []);

  const loadTests = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const runsResponse = await runApi.getAll();
      const runs = runsResponse.data;
      
      if (!runs || runs.length === 0) {
        setTests([]);
        setLoading(false);
        return;
      }

      const testList: UXTest[] = [];
      const agentPromises = runs.map(run => agentApi.getByRunId(run.run_id));
      
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
    } catch (err) {
      console.error('Error loading tests:', err);
      setError('Failed to load tests');
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
    <div className="flex h-screen bg-[#FAFAFA]">
      {/* Left Sidebar */}
      <div className="w-64 bg-white border-r border-[#E3E3E3] flex flex-col">
        <div className="p-4 border-b border-[#E3E3E3]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#555] w-4 h-4" />
            <Input 
              placeholder="Search" 
              className="pl-10 bg-[#F3F3F5] border-none"
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
                  className={`w-full flex items-center justify-between p-2 rounded-lg text-left transition-colors ${
                    selectedFolder === folder.name 
                      ? 'bg-[#E9EBEF] text-[#1A1A1A]' 
                      : 'text-[#555] hover:bg-[#F3F3F5]'
                  }`}
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                >
                  <span>{folder.name}</span>
                  <span className="text-xs">{folder.count}</span>
                </motion.button>
              ))}
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-[#E3E3E3]">
          <Button 
            onClick={onNewTest}
            className="w-full bg-[#4F46E5] hover:bg-[#4338CA] text-white rounded-xl"
          >
            <Plus className="w-4 h-4 mr-2" />
            New UX Test
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <div className="p-6 border-b border-[#E3E3E3] bg-white">
          <h1 className="text-[#1A1A1A] mb-2">UX Tests</h1>
          <p className="text-[#555]">Run AI agents to test user flows and gather insights</p>
        </div>

        <div className="flex-1 p-6 overflow-auto">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="w-8 h-8 animate-spin text-[#4F46E5]" />
            </div>
          ) : error ? (
            <div className="text-center text-[#555] py-8">
              <p>{error}</p>
              <Button 
                onClick={loadTests}
                className="mt-4"
                variant="outline"
              >
                Retry
              </Button>
            </div>
          ) : tests.length === 0 ? (
            <div className="text-center text-[#555] py-8">
              <p>No tests found. Create your first test to get started.</p>
              <Button 
                onClick={onNewTest}
                className="mt-4 bg-[#4F46E5] hover:bg-[#4338CA] text-white"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Test
              </Button>
            </div>
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
                      className="bg-white rounded-xl p-4 border border-[#E3E3E3] shadow-sm hover:shadow-md transition-shadow cursor-pointer mb-4"
                      onClick={() => onSelectTest(test)}
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h3 className="text-[#1A1A1A] mb-1">{test.title}</h3>
                          <p className="text-[#555] text-sm">{test.question}</p>
                        </div>
                        <div className="flex items-center gap-2 text-[#555] text-sm">
                          <div className={`w-2 h-2 rounded-full ${
                            test.status === 'completed' ? 'bg-green-500' : 
                            test.status === 'running' ? 'bg-yellow-500' : 
                            'bg-red-500'
                          }`}></div>
                          {test.time}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-[#555]" />
                        <div className="flex gap-2 flex-wrap">
                          {test.personas.map((persona, idx) => (
                            <Badge key={idx} className={`${persona.color} border-none text-xs`}>
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