# Technical Specifications & Architecture Details

## System Components Technical Details

### 1. PDF Processor Technical Flow

```mermaid
graph TD
    subgraph PDF_Processing
        A[Input PDF] -->|PyPDF2| B[Raw Text]
        B -->|Custom Cleaner| C[Cleaned Text]
        C -->|Validator| D[Validated Text]
      
        subgraph Error_Handling
            E[Corrupt PDF] -->|Recovery| F[Partial Extract]
            G[Password Protected] -->|Skip| H[Error Log]
        end
      
        subgraph Text_Processing
            I[Remove Headers] -->|Clean| J[Strip Artifacts]
            J -->|Format| K[Standardize Text]
        end
    end
```

### 2. LLM Processor Architecture

```mermaid
graph LR
    subgraph LLM_Pipeline
        A[Input Text] -->|Chunk| B[Text Segments]
        B -->|Queue| C[Processing Queue]
      
        subgraph API_Handler
            D[Rate Limiter] -->|Process| E[API Call]
            E -->|Retry Logic| F[Response]
        end
      
        C -->|Submit| D
        F -->|Merge| G[Combined Response]
        G -->|Validate| H[Final Output]
      
        subgraph Error_Recovery
            I[Timeout] -->|Retry| J[Backoff]
            K[API Error] -->|Alternative| L[Fallback]
        end
    end
```

### 3. CIVIC Extractor Component Design

```mermaid
graph TD
    subgraph Data_Processing
        A[LLM Output] -->|Parse| B[JSON Structure]
        B -->|Validate| C[CIVIC Format]
      
        subgraph Validation
            D[Schema Check] -->|Verify| E[Data Types]
            E -->|Check| F[Required Fields]
            F -->|Assess| G[Data Quality]
        end
      
        subgraph Confidence_Scoring
            H[Evidence Level] -->|Weight| I[Score]
            J[Data Completeness] -->|Factor| I
            K[Source Quality] -->|Impact| I
        end
      
        C -->|Score| I
        I -->|Output| L[Final Data]
    end
```

## Component Technical Specifications

### 1. PDF Processor Specifications

#### Input Handling

```python
class PDFProcessor:
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    SUPPORTED_FORMATS = ['.pdf']
    CHUNK_SIZE = 1024 * 1024  # 1MB chunks
  
    TEXT_CLEANING_RULES = {
        'remove_headers': True,
        'strip_numbers': False,
        'normalize_spaces': True,
        'remove_citations': False
    }
```

#### Performance Parameters

- Maximum file size: 100MB
- Processing speed: ~1MB/second
- Memory usage: <500MB
- Concurrent files: Up to 5

### 2. LLM Processor Specifications

#### API Configuration

```python
class LLMConfig:
    MAX_TOKENS = 4000
    TEMPERATURE = 0.0
    TOP_P = 1.0
    FREQUENCY_PENALTY = 0.0
    PRESENCE_PENALTY = 0.0
  
    RETRY_ATTEMPTS = 3
    RETRY_DELAY = [1, 2, 4]  # Exponential backoff
  
    RATE_LIMITS = {
        'requests_per_minute': 50,
        'tokens_per_minute': 100000
    }
```

#### Rate Limiting Strategy

```mermaid
graph TD
    A[Request] -->|Check| B{Rate Limit}
    B -->|Under Limit| C[Process]
    B -->|Over Limit| D[Queue]
    D -->|Wait| E{Retry}
    E -->|Success| C
    E -->|Fail| F[Error]
```

### 3. CIVIC Extractor Specifications

#### Data Model Requirements

```python
class ValidationRules:
    REQUIRED_FIELDS = {
        'variants': ['name', 'type', 'significance'],
        'clinical_evidence': ['type', 'significance'],
        'molecular_data': ['pathway', 'alterations']
    }
  
    CONFIDENCE_WEIGHTS = {
        'evidence_quality': 0.4,
        'data_completeness': 0.3,
        'source_reliability': 0.3
    }
```

#### Validation Flow

```mermaid
stateDiagram-v2
    [*] --> InputValidation
    InputValidation --> SchemaCheck
    SchemaCheck --> DataTypeCheck
    DataTypeCheck --> RequiredFields
    RequiredFields --> QualityCheck
  
    QualityCheck --> PassedValidation
    QualityCheck --> FailedValidation
  
    PassedValidation --> ConfidenceScoring
    FailedValidation --> ErrorHandling
  
    ConfidenceScoring --> [*]
    ErrorHandling --> [*]
```

## System Integration Details

### 1. Component Communication

```mermaid
sequenceDiagram
    participant PDF as PDF Processor
    participant LLM as LLM Processor
    participant CIVIC as CIVIC Extractor
    participant DB as Data Store

    PDF->>PDF: Validate & Clean
    PDF->>LLM: Send Chunks
    activate LLM
    LLM->>LLM: Process & Merge
    LLM->>CIVIC: Structured Data
    deactivate LLM
  
    activate CIVIC
    CIVIC->>CIVIC: Validate
    CIVIC->>CIVIC: Score Confidence
    CIVIC->>DB: Store Results
    deactivate CIVIC
```

### 2. Error Recovery Strategy

```mermaid
flowchart TD
    A[Error Detected] --> B{Error Type}
    B -->|PDF Error| C[PDF Recovery]
    B -->|API Error| D[API Recovery]
    B -->|Validation Error| E[Data Recovery]
  
    C -->|Success| F[Continue]
    C -->|Fail| G[Log & Skip]
  
    D -->|Retry| H[API Call]
    D -->|Max Retries| I[Fallback]
  
    E -->|Fix| J[Revalidate]
    E -->|Cannot Fix| K[Partial Save]
```

## Performance Optimizations

### 1. Memory Management

```mermaid
graph TD
    A[Input] -->|Stream| B[Buffer]
    B -->|Process| C[Release]
  
    subgraph Memory_Pool
        D[Active Memory] -->|Monitor| E[Cleanup]
        E -->|Threshold| F[GC]
    end
```

### 2. Processing Pipeline

```mermaid
graph LR
    subgraph Pipeline
        direction LR
        A[Input] -->|Async| B[Process]
        B -->|Batch| C[Output]
    end
  
    subgraph Optimization
        D[Cache] -->|Hit| E[Quick Return]
        D -->|Miss| F[Full Process]
    end
```
