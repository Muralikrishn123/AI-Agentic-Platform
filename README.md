# 🤖 Reusable Agentic AI Platform (v3.0 - Stable)

A modular, production-grade Multi-Agent AI Platform designed to dynamically plan, qualify, enrich, and generate insights for any B2B business domain. This platform decouples search requirements from static SaaS models, allowing users to define custom qualification rules, create custom domain plugins, monitor collaborative agents in real-time, and converse with a context-aware Voice & Chat Assistant.

---

## 📽️ Submission Deliverables

*   🎥 **[5-Minute Demo Video](https://github.com/Muralikrishn123/AI-Agentic-Platform)** (Showcasing Platform & B2B Lead Generation Use Case)
*   🏗️ **[5-Minute Architecture Walkthrough](ARCHITECTURE_WALKTHROUGH.md)** (Step-by-step numbered guide explaining design decisions, registries, and dynamic routing)
*   📐 **[Architecture Design Document](ARCHITECTURE.md)** (Full technical documentation with sequence diagrams and qualification formulas)
*   📋 **[Requirements & Setup Guide](REQUIREMENTS.md)** (Everything needed to install and run the platform from scratch)
*   💻 **[GitHub Repository Source Code](https://github.com/Muralikrishn123/AI-Agentic-Platform)** (Fully structured documentation & setup instructions)

---

## 🌟 Key Features & UX Innovation

### 1. Dynamic Planner & Capability-Based Routing
The **Planner Agent** parses natural language queries (e.g., *"Find solar leads in Mumbai"*) and consults the **Capability Registry** to map steps dynamically. If a specialized domain plugin is installed and enabled, it routes the workflow there; otherwise, it executes a generic B2B pipeline fallback.

### 2. Domain-Agnostic Configurations
Configure search criteria for *any* business domain under **ICP & Config**:
*   **Organization Types**: Multi-select suggestions (Hospital, University, Factory, Startup, NGO).
*   **Target Geographies & Keywords**: Dynamic, free-form inputs.
*   **Dynamic Size Ranges**: Specify bounds with a custom unit (e.g., `employees`, `beds`, `students`, `sq ft`, `researchers`).
*   **Persona Hierarchy**: Specify target departments and seniority levels for contact discovery.

### 3. Custom Business Domains (Plugins)
Create specialized business rules on the **Plugins** tab:
*   Add custom plugins dynamically (e.g., *"Solar energy sales"*, *"Healthcare systems"*).
*   Input custom qualification requirements (e.g., *"Must have open roof space"*, *"Must use legacy EHR systems"*).
*   Toggle plugins on or off with local fallback triggers.

### 4. Interactive Loading & Results Pipeline
*   **Animated Progress Tracker**: Shows live agent lifecycle stages (Planner → Research → Qualification → Contact Discovery → Reflection → Report).
*   **Active Indicator Badges**: Shows state transitions (Pending ⚪, Running 🔵, Done 🟢) with live elapsed timers.
*   **Export Options**: Generates structured summaries (TXT download) and full prospect lists (CRM-compatible CSV).

### 5. AI Chatbot & Voicebot Assistant
A persistent conversational helper embedded across the application:
*   **Context-Aware Explanations**: Detects the active workflow and answers results-based questions (e.g., *"Why did IIT Bombay match?"*, *"Explain the qualification logic for candidate X"*).
*   **🎤 Voice Input**: Dictate search queries directly using Web Speech recognition.
*   **🔊 Voice Feedback**: Text-to-speech synthesis reads bot responses aloud.
*   **Quota Fallback**: Gracefully serves local FAQs and setup guides if Gemini API limits are hit, avoiding network failures.

---

## 🏗️ Platform Design & Architecture (70% Evaluation Weight)

This platform implements an advanced multi-agent orchestration pattern built around core pillars of reusability, modularity, and human-in-the-loop state safety.

### 1. Agent & Tool Registries
Rather than tightly coupling agents to specific plugins, all agents and tools are registered in centralized registries. 
*   **Reusability**: Tools (e.g., Search, Scraper, Email Finder) are registered as generic capabilities.
*   **Extensibility**: Any new plugin can declare a dependency on a capability (like `contact_discovery`), allowing the platform to dynamically assign agents at runtime.

### 2. Orchestration & State Memory
*   **Orchestration Engine**: A state-machine based workflow engine executes planned sequences.
*   **Execution Memory**: A centralized MongoDB collections schema keeps a persistent, immutable timeline of steps, input configurations, agent outputs, and system logs.
*   **HITL (Human-in-the-Loop) Checkpoint**: Before completing contact discovery or sending outreach, the system can enforce a `pending` state, allowing administrators to review and approve matches via the **Approvals** page.

### 3. Resiliency & Quota Management
The LLM Provider layer implements a robust multi-model fallback list (`gemini-2.5-flash` → `gemini-2.5-flash-lite` → `gemini-2.0-flash`) combined with dynamic backoff retry logic. If the daily API limit is hit, local heuristic fallbacks instantly take over to compile reports and suggest matches.

---

## 💼 Business Use Case & Outcomes (30% Evaluation Weight)

The platform is designed to optimize **B2B Customer Discovery and Lead Qualification** across diverse enterprise verticals:

### 1. Domain Modeling Examples
*   **Solar Energy Vertical**:
    *   *ICP config*: Target type `Factory/Industrial`, keywords `Rooftop, Net-Metering`.
    *   *Custom requirements*: `Must have >10,000 sq ft roof space; must have high electricity expenditures`.
*   **Healthcare Equipment Vertical**:
    *   *ICP config*: Target type `Hospital`, size unit `beds` (range: `100 - 500`).
    *   *Custom requirements*: `Must have active ICU department; must be upgrading diagnostic tools`.

### 2. Customer Discovery Workflow
1.  **Ingestion**: Natural language search query is mapped to a domain configuration.
2.  **Entity Discovery**: Research agents scrape regional registries and web indexes to locate candidate organizations.
3.  **Qualification Filtering**: Evaluates targets against the ICP criteria and custom requirements, grading prospects from `0% to 100%`.
4.  **Enrichment**: Identifies decision-maker personas (e.g., *Head of Facilities*, *Chief Medical Officer*) and locates corporate emails.
5.  **Outcomes**: The resulting CSV export maps directly into CRM pipelines (HubSpot, Salesforce) with custom matching rationales pre-populated.

---

## 🧬 System Architecture Diagram

![System Architecture](platform_architecture.png)

```
                 [ User Search Request ]
                           │
                           ▼
                  [ Planner Agent ]
                           │
        ┌──────────────────┴──────────────────┐
        ▼                                     ▼
[ Dynamic Domain Plugin ]           [ Generic Fallback Plugin ]
(HR, Sales, Custom)                 (Domain-Agnostic Discovery)
        │                                     │
        └──────────────────┬──────────────────┘
                           ▼
               [ Execution Pipeline ]
    ┌──────────────────────┼──────────────────────┐
    ▼                      ▼                      ▼
[ Research ]        [ Qualification ]    [ Contact Discovery ]
 (Scraping)         (Config Scoring)     (Persona Search)
    │                      │                      │
    └──────────────────────┬──────────────────────┘
                           ▼
               [ Validation & Reflection ]
                           │
                           ▼
                  [ Report Generator ]
                           │
                           ▼
                 [ Output & Chatbot ]
```

---

## 🛠️ Technology Stack

*   **Frontend**: React 18, Vite, Vanilla CSS (Glassmorphism & Dark Mode styling), Axios, Web Speech API.
*   **Backend**: Python 3.9+, FastAPI, Uvicorn, MongoDB (Atlas).
*   **AI Integration**: Abstraction-layered LLM Provider using Google Gemini. Includes automatic retry/backoff wrappers.

---

## 🚀 Installation & Setup

### Prerequisites
*   Node.js (v18+)
*   Python (3.9+)
*   MongoDB (Atlas connection string or local instance)

### 1. Backend Setup
1.  Navigate to the `backend` folder:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure environment variables. Create a `.env` file in the `backend` directory:
    ```ini
    MONGODB_URL=your-mongodb-connection-string
    DATABASE_NAME=agentic_platform
    SECRET_KEY=your-jwt-signing-secret
    GEMINI_API_KEY=your-gemini-api-key
    ENVIRONMENT=development
    LOG_LEVEL=INFO
    ```
5.  Start the backend server:
    ```bash
    run_backend.bat
    ```
    The server will start at `http://localhost:8001`.

### 2. Frontend Setup
1.  Navigate to the `frontend` folder:
    ```bash
    cd frontend
    ```
2.  Install packages:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
    The client will start at `http://localhost:5173`.

---

## 📄 License
This project is licensed under the MIT License.
