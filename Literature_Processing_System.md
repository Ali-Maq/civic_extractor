```mermaid
graph TB
    subgraph Frontend
        UI[Web Interface]
        API[RESTful API]
    end

    subgraph Processing Core
        PDF[PDF Processor]
        LLM[LLM Service]
        VM[Validation Manager]
        JQ[Job Queue]
    end

    subgraph Storage
        S3[(AWS S3)]
        ES[(Elasticsearch)]
        Cache[(Redis Cache)]
    end

    subgraph Monitoring
        Logger[Logging Service]
        Metrics[Metrics Collector]
        Alerts[Alert Manager]
    end

    UI -->|Upload| API
    API -->|Queue| JQ
    JQ -->|Process| PDF
    PDF -->|Extract| LLM
    LLM -->|Validate| VM
    VM -->|Store| S3
    VM -->|Index| ES
    
    PDF -.->|Log| Logger
    LLM -.->|Log| Logger
    VM -.->|Log| Logger
    Logger -->|Alert| Alerts
