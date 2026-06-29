# 🎬 5-Minute Architecture Walkthrough Script (Presenter Guide)

This guide provides a step-by-step presentation script corresponding exactly to the numbered steps in the system architecture diagram. Use this to record your **5-minute Architecture Walkthrough Video**.

---

## 📽️ Presenter Roadmap & Script

### Introduction (0:00 - 0:30)
> *"Hello. Today I will walk you through the architectural design of the Reusable Agentic AI Platform. We have structured the system into five modular, decoupled layers to optimize reusability, orchestration integrity, and user experience. 
> 
> Let's trace how data moves through this architecture step-by-step."*

---

### Step 1: User Request Ingestion (0:30 - 1:15)
*   **On Screen**: Point to **Client Layer** (Blue) connecting to **API Gateway Layer** (Purple).
*   **Numbered Path**: `[1] User Query & Config`
> *"**Step 1:** The user enters a search query on the Dashboard and defines their ideal target profile under settings. The React client packages these parameters as a JSON payload and transmits them to our FastAPI backend gateway via HTTP requests, secured by JWT bearer authorization."*

---

### Steps 2 & 3: Workflow Trigger & Capability Resolution (1:15 - 2:00)
*   **On Screen**: Point to **API Gateway** connecting to **Orchestration Engine** (Pink).
*   **Numbered Path**: `[2] Trigger Workflow` and `[3] Resolve Capabilities`
> *"**Step 2:** The API gateway triggers the Workflow Engine. 
>
> **Step 3:** Instead of hardcoding execution paths, the engine consults our Capability, Agent, and Tool registries. It dynamically maps dependencies by matching request goals to available capabilities, deciding which specialized domain agent to execute."*

---

### Steps 4 & 5: Multi-Agent Execution & Domain Logic (2:00 - 3:00)
*   **On Screen**: Point to **Orchestration Engine** connecting to **Execution Layer** (Orange).
*   **Numbered Path**: `[4] Orchestrate Agents` and `[5] Execute Tools`
> *"**Step 4:** The Registry spins up the collaborative agent loop—directing the Planner Agent, Validation Agent, and Reflection Agent.
>
> **Step 5:** The engine activates our Dynamic Domain Plugins—such as B2B Sales, HR recruitment, or custom user plugins. Heuristics are executed, scraping data and filtering matches according to our dynamic weight scoring rules."*

---

### Steps 6 & 7: LLM Reasoning & Refinement (3:00 - 3:45)
*   **On Screen**: Point to **Execution Layer** connecting to **Core Integration Providers** (Green).
*   **Numbered Path**: `[6] LLM Evaluation` and `[7] LLM Reasoning`
> *"**Step 6 & 7:** During execution, both the core agents and plugins leverage our LLM Provider Abstraction layer to query Google Gemini. This layer implements automatic retry backoffs and fails over automatically if any API limit or daily quota is reached, ensuring high platform availability."*

---

### Steps 8 & 9: DB Persistence & Output (3:45 - 4:15)
*   **On Screen**: Point to **Engine/Execution** connecting to **Database** (Green).
*   **Numbered Path**: `[8] Persist Execution State` and `[9] Write Matches`
> *"**Step 8 & 9:** As tasks are completed, the Workflow Engine serializes the progress and writes the execution state to MongoDB. The plugin writes qualified candidate profiles and match scores directly to the database, ensuring memory is preserved."*

---

### Steps 10, 11 & 12: Contextual AI Assistant (4:15 - 5:00)
*   **On Screen**: Point to **Assistant Bot** (Blue) connecting to **API Gateway** and then to **Database & LLM**.
*   **Numbered Path**: `[10] Ask Questions` -> `[11] Fetch Contextual Lead Data` -> `[12] Contextual LLM Explain`
> *"**Step 10:** Finally, when a user interacts with the Chat or Voice Assistant in the frontend, the query is dispatched to the chatbot router.
>
> **Step 11 & 12:** The backend fetches the target workflow matches from MongoDB and passes them as rich system context to Gemini, generating natural-language explanations of *why* candidates qualified.
>
> This clean, decoupled structure ensures that any business plugin can be registered and executed seamlessly. Thank you."*
