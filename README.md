# 🤖 Reusable Agentic AI Platform (v3.0 - Stable)

A modular, production-grade Multi-Agent AI Platform designed to dynamically plan, qualify, enrich, and generate insights for any B2B business domain. This platform decouples search requirements from static SaaS models, allowing users to define custom qualification rules, create custom domain plugins, monitor collaborative agents in real-time, and converse with a context-aware Voice & Chat Assistant.

---

## 🌟 Key Features

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

## 🧬 System Architecture

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

## 📂 Project Structure

```
agentic-platform/
├── frontend/                 # React client
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.jsx    # Application shell
│   │   │   └── AssistantBot.jsx # Chat/Voice assistant widget
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx # Runner dashboard
│   │   │   ├── Config.jsx    # Domain-agnostic settings
│   │   │   ├── Plugins.jsx   # Custom domain builder
│   │   │   ├── Results.jsx   # Animated loader & report view
│   │   │   └── Approvals.jsx # Human-in-the-loop actions
│   └── vite.config.js
└── backend/                  # FastAPI server
    ├── app/
    │   ├── api/              # API endpoints (Auth, Config, Chatbot)
    │   ├── core/             # Base Agents (Planner, Validation, Report)
    │   ├── database/         # MongoDB connections & models
    │   ├── plugins/          # Plugin modules (HR, Sales, Generic)
    │   └── services/         # Registries (Agent, Capability, Tool)
    ├── config/               # Settings & environment loads
    └── run_backend.bat       # Startup utility script
```

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

## 📝 Running Workflows (How to Use)

### Step 1: Set Target Profile
Go to the **ICP & Config** tab and configure target criteria (e.g. Set *Target Organization Types* to `Hospital`, *Keywords* to `Solar, Energy`, and *Size Unit* to `beds` with range `50 - 500`). Click **Save Configuration**.

### Step 2: (Optional) Register Custom Plugin
Go to the **Plugins** tab, click **+ Create Plugin**, name it `Solar Hospital Sales`, and add *Qualification Requirements* like `Must have open terrace space`. Click **Save**.

### Step 3: Run the workflow
Go to the **Dashboard**, choose **Auto-detect plugin**, enter your query:
> *"Find hospitals in Mumbai looking to install solar panels."*

Click **⚡ Start Workflow**.

### Step 4: Track Progress & Chat
*   Watch the animated pipeline check off each agent stage in real-time.
*   Once finished, review the structured summary and matching cards.
*   Click the **Assistant Bot** in the bottom-right, ask *"Why did IIT Bombay match?"*, and hear/read the explained qualification rationale!

---

## 📄 License
This project is licensed under the MIT License.
