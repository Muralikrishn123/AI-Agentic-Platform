# 🤖 Reusable Agentic AI Platform (v3.0 - FINAL)

> The ultimate production-grade, extensible multi-agent platform with Capability Registry, Event Bus, and complete Plugin Lifecycle Management

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)
[![Architecture](https://img.shields.io/badge/architecture-v3.0-green.svg)](ARCHITECTURE_V3_FINAL.md)
[![Rating](https://img.shields.io/badge/rating-10%2F10-brightgreen.svg)](ARCHITECTURE_V3_FINAL.md)

## 🔒 Status: LOCKED & READY

**Architecture:** FROZEN ❄️  
**Design Phase:** COMPLETE ✅  
**Implementation:** READY TO START 🚀  
**Rating:** 10/10  

### 🚫 No More Architecture Discussions

From this point forward:
- ✅ Implementation questions only
- ✅ "Let's build [component]"
- ❌ "Should we change [architecture]?"
- ❌ Any design discussions

📚 **See:** [LOCKED.md](LOCKED.md) for communication rules

---

**Core (Implement First):**
- ✅ **Agent Registry** - Central agent management
- ✅ **Capability Registry** - Capability-based routing ⭐
- ✅ **Tool Registry** - Central tool management
- ✅ **Workflow Engine** - Orchestration
- ✅ **Plugin Lifecycle Manager** - Full plugin lifecycle ⭐
- ✅ **LLM Provider** - Provider abstraction
- ✅ **Memory Service** - State management

**Advanced (Add When Needed):**
- ⏸️ **Event Bus** - Event-driven architecture (optional)
- ⏸️ **Reflection Agent** - Quality evaluation (optional)
- ⏸️ **Configuration Manager** - Runtime config (optional)

📚 **Read:**
- [ARCHITECTURE_FROZEN.md](ARCHITECTURE_FROZEN.md) - **Architecture is frozen** ⭐
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - **Week-by-week plan** ⭐
- [ARCHITECTURE_V3_FINAL.md](ARCHITECTURE_V3_FINAL.md) - Complete design

## Architecture Overview (v3.0 - FINAL)

```
User Request
    ↓
Planner Agent (plans with CAPABILITIES)
    ↓
Capability Registry (resolves to agents)
    ↓
Workflow Engine (executes via Event Bus)
    ↓
Plugin Lifecycle Manager
    ↓
Plugin Execution
    ↓
Reflection Agent (evaluate & retry)
    ↓
Validation Agent
    ↓
Report Generator
    ↓
Event Bus (notifies dashboard, logger)
```

## Technology Stack

### Frontend
- React (Vite)
- Tailwind CSS
- React Router
- Axios

### Backend
- Python
- FastAPI
- MongoDB

### AI Framework
- LLM Provider abstraction layer
- Initially: Gemini API
- Deployment: OpenAI API

## Project Structure

```
agentic-platform/
├── frontend/          # React application
└── backend/           # FastAPI application
    ├── app/
    │   ├── api/       # API routes
    │   ├── core/      # Core agents and services
    │   ├── database/  # Database models and connections
    │   ├── plugins/   # Plugin system (empty initially)
    │   └── services/  # Business logic services
    └── config/        # Configuration files
```

## Core Components

### Agents (All reusable, registered in Agent Registry)

1. **Planner Agent** - Breaks user requests into executable workflows
2. **Validation Agent** - Validates outputs (missing fields, invalid JSON, confidence)
3. **Reflection Agent** - Evaluates workflow success, decides on retries
4. **Report Generator** - Converts workflow results into structured reports (JSON-first)

### Services

- **Agent Registry** - Central registry for platform + plugin agents
- **Tool Registry** - Central registry for all tools
- **Tool Executor** - Executes tools with logging and monitoring
- **Memory Service** - Stores workflow state and agent outputs
- **Plugin Manager** - Manages plugin lifecycle

## Phase 1 Scope (v2.0)

✅ Generic platform infrastructure  
✅ Agent Registry (central agent management)  
✅ Tool Registry + Tool Executor  
✅ Memory Service (not agent)  
✅ Core agents (Planner, Validation, Reflection, Report Generator)  
✅ Workflow engine  
✅ Plugin manager  
✅ Authentication  
✅ Dashboard UI  

❌ Domain-specific plugins (Phase 2)

## Getting Started

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

Once running, visit: http://localhost:8000/docs

## Environment Variables

Create a `.env` file in the backend directory:

```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=agentic_platform
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
```

## License

MIT
