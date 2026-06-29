import base64
import urllib.request
import os

MERMAID_DIAGRAM = """graph TB
    subgraph ClientLayer [Client Layer - React Client]
        UI[Dashboard & Settings UI]
        AB[AssistantBot Chat & Voice]
    end

    subgraph APILayer [API Layer - FastAPI Routers]
        AUTH[Auth Router]
        WORK[Workflow Router]
        PLUG[Plugins Router]
        CONF[Config Router]
        CHAT[Chatbot Router]
    end

    subgraph CoreOrchestration [Core Orchestration Engine]
        WE[Workflow Engine]
        REGA[Agent Registry]
        REGC[Capability Registry]
        REGT[Tool Registry]
    end

    subgraph AI_Agents [Collaborative AI Agents]
        PLAN[Planner Agent]
        VAL[Validation Agent]
        REFL[Reflection Agent]
        REP[Report Generator]
        HITL[HITL Approval Agent]
    end

    subgraph Plugins [Dynamic Domain Plugins]
        B2B[B2B Sales Plugin]
        HR[HR Recruitment Plugin]
        GEN[Generic Domain Plugin]
    end

    subgraph Tools [Tool Executions Layer]
        SCRAPE[Web Scraper Tool]
        SCORE[ICP Scoring Engine]
        EMAIL[Email Finder Tool]
    end

    subgraph LLMProvider [LLM Provider Layer]
        LP[LLM Provider Abstraction]
        GEM[Gemini Provider]
    end

    subgraph Database [Data Store]
        DB[(MongoDB Database)]
    end

    UI --> AUTH
    UI --> WORK
    UI --> PLUG
    UI --> CONF
    AB --> CHAT

    WORK --> WE
    WE --> REGC
    WE --> REGA
    WE --> REGT

    REGA --> PLAN
    REGA --> VAL
    REGA --> REFL
    REGA --> REP
    REGA --> HITL

    PLUG --> B2B
    PLUG --> HR
    PLUG --> GEN

    REGT --> SCRAPE
    REGT --> SCORE
    REGT --> EMAIL

    PLAN --> LP
    B2B --> LP
    HR --> LP
    REFL --> LP
    CHAT --> LP
    LP --> GEM
    
    WE --> DB
    CHAT --> DB
    B2B --> DB
    HR --> DB"""

def generate_diagram_image():
    print("Encoding Mermaid diagram...")
    graph_bytes = MERMAID_DIAGRAM.encode("utf8")
    base64_bytes = base64.urlsafe_b64encode(graph_bytes)
    base64_string = base64_bytes.decode("ascii")
    
    url = f"https://mermaid.ink/img/{base64_string}"
    
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "platform_architecture.png"))
    print(f"Downloading visual diagram from: {url}")
    print(f"Saving to: {output_path}")
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            with open(output_path, "wb") as f:
                f.write(response.read())
        print("Success! Clean architecture diagram PNG created successfully.")
    except Exception as e:
        print(f"Error downloading image: {e}")

if __name__ == "__main__":
    generate_diagram_image()
