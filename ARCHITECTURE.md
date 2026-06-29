# 🏗️ Multi-Agent Platform Architecture Design

This document details the key architectural and design decisions behind the **Agentic AI Platform (v3.0)**, mapping directly to the grading criteria for platform extensibility, reusability, memory orchestration, and user experience.

---

## 1. Core Architectural Pillars

The platform is designed around three fundamental concepts: **Capability-Based Routing**, **Domain Decoupling**, and **Stateless Executions with Persistent DB Memory**.

```mermaid
graph TD
    subgraph Frontend (React 18 + Vite)
        A[Dashboard / Config UI] -->|User Input| C[AssistantBot Chat]
        B[Results UI / Animated Loader] -->|Context| C
    end

    subgraph Backend (FastAPI API Layer)
        C -->|POST /api/chatbot/query| D[Chatbot Router]
        A -->|POST /api/workflow/start| E[Workflow Router]
        E -->|Get Capabilities| F[Capability Registry]
    end

    subgraph Core Orchestration Engine
        E -->|Orchestrate| G[Workflow Engine]
        G -->|1. Plan| H[Planner Agent]
        G -->|2. Run| I[Plugin Lifecycle Manager]
        I -->|Init / Run| J[Domain Plugin]
        G -->|3. Validate| K[Validation Agent]
        G -->|4. Reflect| L[Reflection Agent]
        G -->|5. Compile| M[Report Generator]
    end

    subgraph LLM Provider Layer
        H & J & L & M & D -->|Query Prompt| N[Gemini Provider]
        N -->|Retry Backoff Loop| O[Generative AI API]
    end

    subgraph Database (MongoDB Atlas)
        G & D & I -->|Read / Write| P[(MongoDB Collections)]
    end

    style G fill:#4f46e5,stroke:#4338ca,color:#fff
    style N fill:#0891b2,stroke:#0891b2,color:#fff
    style P fill:#10b981,stroke:#059669,color:#fff
```

---

## 2. Platform Evaluation Criteria Mappings (70% Weight)

### 🚀 Reusability and Extensibility
*   **Decoupled Domain Schemas**: The platform has no hardcoded SaaS variables (e.g., funding stages or employee size constraints). Instead, configurations (organization types, size ranges, units, and custom requirements) are fully dynamic.
*   **The Plugin Lifecycle Manager**: Handles installing, initializing, enabling, and disabling domain-specific plugins (like `hr_recruitment`, `b2b_sales`, or custom configurations) on the fly without restarting the server.
*   **Capability Registry**: Tools are treated as generic capabilities (e.g., `web_scraping`, `contact_discovery`). When a new plugin runs, the Planner resolves these capability tags to specialized agents in the registry.

### 🧠 Memory and Orchestration Design
*   **Stateless Workflow Engine**: The engine runs workflows using step-by-step state-machines. Individual agents perform stateless runs and return their outcomes to the main loop.
*   **Persistent MongoDB State**: The workflow execution state is immediately serialized and persisted into MongoDB at each step. This acts as the platform's long-term memory.
*   **HITL (Human-in-the-Loop) Checkpoint**: If a workflow state transitions to `hitl_pending`, execution freezes. The backend preserves the context until an approval signal is received from the **Approvals** tab, at which point the workflow resumes.

### 🛡️ Resiliency and Quota Handling
To prevent rate-limit crashes under heavy utilization:
1.  **Model Fallback List**: Generates text using a tier list (`gemini-2.5-flash` → `gemini-2.5-flash-lite` → `gemini-2.0-flash`). If one is rate-limited, it automatically fails over to the next model.
2.  **Backoff sleep**: Automatically parses the Google API `retryDelay` headers and pauses execution before retrying.
3.  **Local Fallback System**: If all LLM options fail, local heuristic parsers run automatically, generating output reports using offline analytics and database templates.

---

## 3. Conversational Context & Speech Architecture

The Chatbot and Voicebot features are designed to bridge the user interface directly with database memory and system-level rules:

```
[User Chat Speech]
       │
       ▼ (SpeechRecognition API)
[Text Query] + [Active Workflow ID]
       │
       ▼ (POST /api/chatbot/query)
[FastAPI Backend Router]
       │
       ├─► Queries MongoDB for Workflow ID
       │   (Fetches User query, report summary, prospects list & reasons)
       │
       ▼
[Context-Aware Gemini Prompt]
       │
       ▼
[Generated Answer]
       │
       ├─► (Frontend UI Render)
       │
       ▼ (SpeechSynthesis API)
[Out-Loud Audio Voice Feedback]
```

### Key Technical Specs:
*   **Web Speech Recognition**: Uses browser-native speech recognition (`window.webkitSpeechRecognition`). Filters ambient noise and outputs inline text into the user input element.
*   **Web Speech Synthesis**: Uses browser-native speech synthesis (`window.speechSynthesis`). Automatically strips markdown characters (`*`, `#`, `_`) to ensure smooth, natural reading patterns.
*   **Local Quota Safeguard**: If Gemini API limits are hit during chat, the backend switches to a local FAQ directory. It evaluates the user's query against local keywords (e.g. "plugin", "ICP", "why") and responds with helper articles.
