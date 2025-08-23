'use client';

import { useState } from 'react';
import { Dashboard } from '@/components/Dashboard';
import { TestSetupWizard } from '@/components/TestSetupWizard';
import { SwarmProgress } from '@/components/SwarmProgress';
import { TranscriptView } from '@/components/TranscriptView';
import { UXReport } from '@/components/UXReport';
import { AskTheData } from '@/components/AskTheData';
import { TicketModal } from '@/components/TicketModal';
import { Breadcrumb } from '@/components/Breadcrumb';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Share, MoreVertical, FileDown, Mail, Link } from 'lucide-react';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { motion, AnimatePresence } from 'framer-motion';
import { runApi } from '@/lib/api';
import { toast } from 'sonner';

type ViewType = 'dashboard' | 'test-results';

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

export default function Home() {
  const [currentView, setCurrentView] = useState<ViewType>('dashboard');
  const [showSetup, setShowSetup] = useState(false);
  const [showProgress, setShowProgress] = useState(false);
  const [showTicketModal, setShowTicketModal] = useState(false);
  const [activeTab, setActiveTab] = useState('transcript');
  const [currentTest, setCurrentTest] = useState<any>(null);
  const [testConfig, setTestConfig] = useState<TestConfig | null>(null);
  const [selectedInsight, setSelectedInsight] = useState<any>(null);

  const handleNewTest = () => {
    setShowSetup(true);
  };

  const handleSelectTest = (test: any) => {
    setCurrentTest(test);
    setCurrentView('test-results');
    setActiveTab('transcript');
  };

  const handleRunTest = async (config: TestConfig) => {
    try {
      // Transform the personas to match the API format
      const personas = config.personas.map(p => ({
        name: p.name,
        age: p.age,
        context: p.context
      }));

      // Create the run via API
      const response = await runApi.create({
        url: config.url,
        ux_question: config.question,
        selector: config.selector || undefined,
        personas
      });

      console.log('Test started:', response.data);
      
      // Store the config with the run ID
      setTestConfig({
        ...config,
        runId: response.data.run_id
      } as any);
      
      setShowSetup(false);
      setShowProgress(true);
      
      toast.success('Test started successfully!', {
        description: `Running ${config.personas.length} personas on ${config.url}`
      });
    } catch (error: any) {
      console.error('Failed to start test:', error);
      
      // Check if it's a network error (backend not running)
      if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
        toast.error('Backend server is not running', {
          description: 'Please start the backend server on port 8000 to run tests.',
          duration: 5000,
        });
        
        // For demo purposes, offer to run in mock mode
        toast.info('Running in demo mode', {
          description: 'Simulating test execution for demonstration purposes.',
          duration: 3000,
        });
        
        // Generate a mock run ID
        const mockRunId = `demo-${Date.now()}`;
        
        setTestConfig({
          ...config,
          runId: mockRunId
        } as any);
        
        setShowSetup(false);
        setShowProgress(true);
        
        // Auto-complete after 5 seconds for demo
        setTimeout(() => {
          handleProgressComplete();
          toast.success('Demo test completed!', {
            description: 'This was a simulated test run. Start the backend to run real tests.'
          });
        }, 5000);
      } else {
        // Other API errors
        toast.error('Failed to start test', {
          description: error.response?.data?.message || error.message || 'An unexpected error occurred',
          duration: 5000,
        });
      }
    }
  };

  const handleProgressComplete = () => {
    setShowProgress(false);
    setCurrentView('test-results');
    setActiveTab('transcript');
  };

  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
    setCurrentTest(null);
    setTestConfig(null);
  };

  const handleGenerateTicket = (insight: any) => {
    setSelectedInsight(insight);
    setShowTicketModal(true);
  };

  const handleJumpToTranscript = (moment: string) => {
    setActiveTab('transcript');
  };

  const handleSelectInsight = (step: any) => {
    setActiveTab('insights');
  };

  const handleExportMenu = (action: string) => {
    console.log('Export action:', action);
  };

  return (
    <div className="h-screen bg-[#FAFAFA] font-sans">
      <AnimatePresence mode="wait">
        {currentView === 'dashboard' ? (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="h-full"
          >
            <Dashboard
              onNewTest={handleNewTest}
              onSelectTest={handleSelectTest}
            />
          </motion.div>
        ) : (
          <motion.div
            key="test-results"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="h-full flex flex-col"
          >
            {/* Header */}
            <div className="p-4 border-b border-[#E3E3E3] bg-white">
              <div className="mb-3">
                <Breadcrumb 
                  items={[
                    { label: 'Dashboard', href: '/' },
                    { label: currentTest?.title || 'Test Results' }
                  ]} 
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-[#1A1A1A]">
                    {currentTest?.title || 'Test Results'}
                  </h1>
                  <p className="text-sm text-[#555] mt-1">
                    {testConfig?.question || currentTest?.question || 'Analyzing user experience'}
                  </p>
                </div>
              
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-[#E3E3E3] text-[#555] hover:bg-[#F3F3F5]"
                  >
                    <Share className="w-4 h-4 mr-2" />
                    Share
                  </Button>
                  
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="outline" 
                        size="sm"
                        className="border-[#E3E3E3] text-[#555] hover:bg-[#F3F3F5]"
                      >
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-48">
                      <DropdownMenuItem onClick={() => handleExportMenu('copy-link')}>
                        <Link className="w-4 h-4 mr-2" />
                        Copy Link
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => handleExportMenu('export-pdf')}>
                        <FileDown className="w-4 h-4 mr-2" />
                        Export PDF
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => handleExportMenu('export-csv')}>
                        <FileDown className="w-4 h-4 mr-2" />
                        Export CSV
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => handleExportMenu('email-summary')}>
                        <Mail className="w-4 h-4 mr-2" />
                        Email Summary
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            </div>

            {/* Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
              <div className="px-4 py-2 bg-white border-b border-[#E3E3E3]">
                <TabsList className="bg-[#F3F3F5] p-1 rounded-xl">
                  <TabsTrigger 
                    value="transcript" 
                    className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm"
                  >
                    Transcript
                  </TabsTrigger>
                  <TabsTrigger 
                    value="insights" 
                    className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm"
                  >
                    UX Report
                  </TabsTrigger>
                  <TabsTrigger 
                    value="ask-data" 
                    className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm"
                  >
                    Ask the Data
                  </TabsTrigger>
                </TabsList>
              </div>

              <TabsContent value="transcript" className="flex-1 m-0">
                <TranscriptView
                  testConfig={testConfig || currentTest}
                  onSelectInsight={handleSelectInsight}
                />
              </TabsContent>

              <TabsContent value="insights" className="flex-1 m-0">
                <UXReport
                  testConfig={testConfig || currentTest}
                  onGenerateTicket={handleGenerateTicket}
                  onJumpToTranscript={handleJumpToTranscript}
                />
              </TabsContent>

              <TabsContent value="ask-data" className="flex-1 m-0">
                <AskTheData testConfig={testConfig || currentTest} />
              </TabsContent>
            </Tabs>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modals */}
      <TestSetupWizard
        isOpen={showSetup}
        onClose={() => setShowSetup(false)}
        onRunTest={handleRunTest}
      />

      <SwarmProgress
        isOpen={showProgress}
        onClose={() => setShowProgress(false)}
        onComplete={handleProgressComplete}
        testConfig={testConfig}
      />

      <TicketModal
        isOpen={showTicketModal}
        onClose={() => setShowTicketModal(false)}
        insight={selectedInsight}
      />
    </div>
  );
}