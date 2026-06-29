import base64
import urllib.request
import os

MERMAID_DIAGRAM = """graph TD
    subgraph Client [1. Client Layer - React Client]
        UI[Dashboard & Settings Page]
        AB[Voice & Chat Assistant Bot]
    end

    subgraph Gateway [2. API Gateway - FastAPI Routers]
        API[App Routers: Auth, Config, Workflows, Plugins, Chatbot]
    end

    subgraph Engine [3. Orchestration Engine]
        WE[Workflow Engine]
        REG[Registries: Agent, Capability & Tool]
    end

    subgraph Execution [4. Execution Layer - Agents & Plugins]
        AGENTS[Collaborative Agents: Planner, Validation, Reflection, Report]
        PLUGINS[Domain Plugins: B2B Sales, HR, Custom Plugins]
    end

    subgraph Providers [5. Core Integration Providers]
        LP[LLM Provider - Google Gemini]
        DB[(Data Store - MongoDB Atlas)]
    end

    UI -->|JSON Requests| API
    AB -->|Ask Context Query| API
    
    API -->|Init Execution| WE
    WE -->|Resolve Capabilities| REG
    
    REG -->|Orchestrate| AGENTS
    REG -->|Execute| PLUGINS
    
    AGENTS -->|Generate Prompts| LP
    PLUGINS -->|Generate Prompts| LP
    API -->|Query Context| LP
    
    WE -->|Store State / Results| DB
    PLUGINS -->|Fetch/Write| DB
    API -->|Fetch Context| DB

    classDef client fill:#3b82f6,stroke:#1d4ed8,color:#fff;
    classDef gateway fill:#8b5cf6,stroke:#6d28d9,color:#fff;
    classDef engine fill:#ec4899,stroke:#be185d,color:#fff;
    classDef exec fill:#f59e0b,stroke:#d97706,color:#fff;
    classDef provider fill:#10b981,stroke:#059669,color:#fff;

    class UI,AB client;
    class API gateway;
    class WE,REG engine;
    class AGENTS,PLUGINS exec;
    class LP,DB provider;"""

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
        with urllib.request.urlopen(req, timeout=15) as response:
            with open(output_path, "wb") as f:
                f.write(response.read())
        print("Success! Clean architecture diagram PNG created successfully.")
    except Exception as e:
        print(f"Error downloading image: {e}")

if __name__ == "__main__":
    generate_diagram_image()
