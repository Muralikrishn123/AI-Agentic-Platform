# 🏆 Agentic AI Platform — B2B Lead Discovery & Qualification

This repository contains the **Agentic AI Platform**, a reusable, modular multi-agent system designed to dynamically plan, scrape, qualify, and enrich leads for any B2B business domain.

---

## 👥 Team Details
*   **Team Name**: [Insert Team Name]
*   **Team Members**:
    1. [Member 1 Name] - [Member 1 Role/Email]
    2. [Member 2 Name] - [Member 2 Role/Email]
*   **Submission Date**: Monday, 29 June 2026

---

## 🌐 GitHub Repository Link
*   **Repository URL**: [https://github.com/Muralikrishn123/AI-Agentic-Platform/](https://github.com/Muralikrishn123/AI-Agentic-Platform/)

---

## 📝 Project Overview
Traditional B2B discovery platforms are locked to static SaaS schemas (e.g., matching by employee count or industry tags). This platform introduces a **domain-agnostic multi-agent system** with dynamic rule compilation:
*   **Dynamic Planner Agent**: Evaluates natural language queries and automatically plans the execution path by consulting the Capability Registry.
*   **Domain-Agnostic Settings**: Allows users to specify target organization types, free-form keywords, and target size bounds with a customizable unit (e.g., `beds` for hospitals, `sq ft` for real estate, `students` for education).
*   **Custom Domain Plugins**: Allows users to define custom qualification guidelines (e.g., *"Must have open terrace space for solar installation"*) which are parsed and scored dynamically by execution agents.
*   **Animated Results Pipeline**: Real-time visualization of agent progress (Planner → Research → Qualification → Contact Discovery → Reflection → Report) with live status updates.
*   **AI Chatbot & Voicebot**: floating assistant bubble featuring browser-native voice dictation (Speech Recognition) and reading (Speech Synthesis) to explain qualified target match reasons from MongoDB context.

---

## ⚙️ Setup Instructions

### 1. Prerequisites
*   **Node.js**: v18+
*   **Python**: v3.9+
*   **MongoDB**: An active Atlas cluster connection string or local instance.

### 2. Backend Installation & Run
1.  Navigate to the `backend/` directory:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    # On Windows:
    venv\\Scripts\\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```
3.  Install all Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure environment variables. Create a `.env` file in the `backend/` directory:
    ```ini
    MONGODB_URL=your-mongodb-atlas-connection-string
    DATABASE_NAME=agentic_platform
    SECRET_KEY=your-jwt-signing-secret-key
    GEMINI_API_KEY=your-active-gemini-api-key
    ENVIRONMENT=development
    LOG_LEVEL=INFO
    ```
5.  Start the FastAPI server:
    ```bash
    # Windows (sets UTF-8 encoding for command line icons)
    run_backend.bat
    
    # Or manual command:
    python -m uvicorn app.main:app --port 8001
    ```
    The API will run at `http://localhost:8001` (Docs at `/docs`).

### 3. Frontend Installation & Run
1.  Open a new terminal window and navigate to the `frontend/` directory:
    ```bash
    cd frontend
    ```
2.  Install npm packages:
    ```bash
    npm install
    ```
3.  Start the local development server:
    ```bash
    npm run dev
    ```
    Open your browser and navigate to `http://localhost:5173`.

---

## 💡 Additional Notes
*   **Port Mapping**: The frontend is pre-configured via `vite.config.js` to proxy `/api` requests to port `8001`.
*   **API Quota Fallback**: If the Google Gemini daily free-tier API quota is reached during operation, the backend automatically intercepts the error and falls back to a rule-based engine to explain matching metrics, preventing frontend server errors.
*   **Voice Compatibility**: Browser voice input utilizes the HTML5 SpeechRecognition API, which is supported on Google Chrome and Microsoft Edge (Firefox is not supported).
*   **Code Packaging**: For zipping the source code, exclude dependency folders: `node_modules`, `venv`, and local database files.
