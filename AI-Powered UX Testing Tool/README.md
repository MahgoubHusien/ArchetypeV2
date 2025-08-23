# AI-Powered UX Testing Tool - Frontend

A React-based frontend for the UX Testing Tool that allows you to run AI agents to test user flows and gather insights.

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **shadcn/ui** component library
- **Framer Motion** for animations
- **Axios** for API calls

## Setup

### Prerequisites

- Node.js 18+ installed
- Backend API running on http://localhost:8000

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at http://localhost:3000

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
.
├── components/
│   ├── ui/           # shadcn/ui components
│   ├── Dashboard.tsx # Main dashboard view
│   ├── TestSetup.tsx # Test configuration modal
│   ├── SwarmProgress.tsx # Test progress indicator
│   ├── TranscriptView.tsx # Test transcript viewer
│   ├── UXReport.tsx  # UX insights report
│   └── AskTheData.tsx # Query interface
├── services/
│   └── api.ts        # API service layer
├── hooks/
│   └── useApi.ts     # Custom API hook
├── styles/
│   └── globals.css   # Global styles
├── App.tsx           # Main application component
└── main.tsx          # Application entry point
```

## API Integration

The frontend connects to the backend API through a proxy configuration in Vite. All API calls to `/api/*` are proxied to `http://localhost:8000`.

### Available API Endpoints

- **Agents**: `/api/agents`, `/api/agents/{id}`, `/api/agents/by-run/{runId}`
- **Interactions**: `/api/interactions`, `/api/interactions/{id}`, `/api/interactions/by-agent/{agentId}`
- **Runs**: `/api/runs`, `/api/runs/{id}`

## Features

- **Dashboard View**: Browse and manage UX tests
- **Test Creation**: Configure new tests with personas and questions
- **Real-time Progress**: Monitor test execution
- **Transcript View**: Review agent interactions step-by-step
- **UX Report**: Analyze insights and patterns
- **Data Querying**: Ask questions about test results

## Environment Variables

Create a `.env.local` file if you need to override the default API URL:

```
VITE_API_URL=http://your-api-url:8000
```

## Notes

- The app uses mock data when no backend data is available
- All timestamps are automatically formatted
- Persona colors are automatically assigned based on order