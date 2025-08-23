import { useState } from 'react';
import { Dashboard } from './components/Dashboard';
import { TestSetup } from './components/TestSetup';
import { SwarmProgress } from './components/SwarmProgress';
import { TranscriptView } from './components/TranscriptView';
import { UXReport } from './components/UXReport';
import { AskTheData } from './components/AskTheData';
import { TicketModal } from './components/TicketModal';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Button } from './components/ui/button';
import { ArrowLeft, Share, MoreVertical, FileDown, Mail, Link } from 'lucide-react';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './components/ui/dropdown-menu';
import { motion, AnimatePresence } from 'motion/react';

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

export default function App() {
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

  const handleRunTest = (config: TestConfig) => {
    setTestConfig(config);
    setShowSetup(false);
    setShowProgress(true);
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
    // In a real app, you would scroll to the specific timestamp
  };

  const handleSelectInsight = (step: any) => {
    setActiveTab('insights');
  };

  const handleExportMenu = (action: string) => {
    console.log('Export action:', action);
    // Implement export functionality
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
            <div className="p-4 border-b border-[#E3E3E3] bg-white flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button
                  onClick={handleBackToDashboard}
                  variant="ghost"
                  size="sm"
                  className="text-[#555] hover:text-[#1A1A1A]"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Dashboard
                </Button>
                <div>
                  <h1 className="text-[#1A1A1A]">
                    {currentTest?.title || 'Checkout flow confusion analysis'}
                  </h1>
                  <p className="text-sm text-[#555]">
                    {testConfig?.question || currentTest?.question || 'Where do users get confused during checkout?'}
                  </p>
                </div>
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
                    <DropdownMenuItem onClick={() => handleExportMenu('send-notion')}>
                      📝 Send to Notion
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleExportMenu('email-summary')}>
                      <Mail className="w-4 h-4 mr-2" />
                      Email Summary
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
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
      <TestSetup
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