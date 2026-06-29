import base64
import urllib.request
import os

MERMAID_DIAGRAM = """graph TD
    subgraph Frontend [Frontend Layer - React Client]
        Dashboard[B2B Orchestration Dashboard UI]
        ChatbotUI[Clarification Chatbot UI]
    end

    subgraph API [API Layer - FastAPI]
        Gateway[FastAPI Gateway]
        Endpoints["/planner (Run Pipeline)<br/>/feedback (Submit Feedback)<br/>/plugins (Manage Plugins)<br/>/chat (Recommendation Chat)"]
    end

    subgraph Ingestion [Web Engineering Data Ingestion Pipeline]
        Scraper["Scraper Runner<br/>(Playwright / Scrapy / Apify)"]
        Signal["Signal Extractor<br/>(Job listings, News, Tech stacks)"]
        Enrich["Data Enrichment<br/>(Clearbit / Apollo APIs)"]
    end

    subgraph Storage [Storage & Persistence Layer - Unstructured NoSQL Database]
        ProspectDB[(Prospect Database<br/>enriched data)]
        FeedbackMem[(Feedback Memory<br/>accepted/rejected logs)]
        PluginsDB[(Plugins Database<br/>custom overrides)]
        GlobalMem[(Global Memory Database<br/>thresholds)]
    end

    subgraph Orchestration [Orchestration Layer - Multi-Agent DAG]
        Planner["1. Planner Agent (Gemini)"]
        Search["2. Search Agent"]
        Qualify["3. Qualification Agent"]
        Recommend["4. Recommendation Agent (Gemini)"]
    end

    Dashboard <-->|HTTP Requests| Gateway
    ChatbotUI <-->|HTTP Requests| Gateway
    Gateway <--> Endpoints

    Scraper --> Signal
    Signal --> Enrich
    Enrich -->|Bulk Upsert / Stream| ProspectDB

    Endpoints -->|Initial State| Planner
    Planner -->|Domain & Signals| Search
    Search -->|Matched Companies| Qualify
    Qualify -->|Scored & Filtered Prospects| Recommend
    Recommend -->|Outreach Campaigns| Endpoints

    Endpoints -->|Post Feedback / Adjust Weights| FeedbackMem
    Endpoints -->|CRUD Plugins| PluginsDB
    Search -->|Dynamic Query| PluginsDB
    Search -->|Fetch Enriched Data| ProspectDB
    FeedbackMem -->|Syncs state & updates limits| GlobalMem
    Qualify -->|Query Feedback & Thresholds| GlobalMem
    Recommend -->|Query Feedback & Thresholds| GlobalMem

    classDef frontend fill:#2563eb,stroke:#1d4ed8,color:#fff;
    classDef api fill:#16a34a,stroke:#15803d,color:#fff;
    classDef ingestion fill:#ea580c,stroke:#d97706,color:#fff;
    classDef storage fill:#db2777,stroke:#be185d,color:#fff;
    classDef orchestration fill:#9333ea,stroke:#7e22ce,color:#fff;

    class Dashboard,ChatbotUI frontend;
    class Gateway,Endpoints api;
    class Scraper,Signal,Enrich ingestion;
    class ProspectDB,FeedbackMem,PluginsDB,GlobalMem storage;
    class Planner,Search,Qualify,Recommend orchestration;"""

def generate_diagram_image():
    print("Encoding Mermaid diagram...")
    graph_bytes = MERMAID_DIAGRAM.encode("utf8")
    base64_bytes = base64.urlsafe_b64encode(graph_bytes)
    base64_string = base64_bytes.decode("ascii")
    
    url = f"https://mermaid.ink/img/{base64_string}"
    
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Agentic_AI_Platform_Submission", "02_Architecture", "platform_architecture.png"))
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
