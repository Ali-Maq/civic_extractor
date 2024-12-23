# Prompting Strategy & LLM Architecture

## ReACT Prompting Flow

### Stage 1: Initial Analysis

```mermaid
graph TD
    A[Text Input] -->|Parse| B{ReACT Process}
    B -->|Reason| C[Context Analysis]
    B -->|Action| D[Data Extraction]
    B -->|Conclude| E[Synthesis]
    B -->|Think| F[Validation]
```

### Stage 2: Structured Extraction

```mermaid
sequenceDiagram
    participant Text as Input Text
    participant LLM as Claude-3
    participant Parser as JSON Parser
    participant Validator as Data Validator

    Text->>LLM: Send Chunk
    LLM->>LLM: Apply ReACT
    LLM->>Parser: Return JSON
    Parser->>Validator: Validate Structure
    Validator->>Parser: Return Status
```

### Stage 3: Confidence Scoring

```mermaid
graph LR
    A[Raw Score] -->|Weight| B(Evidence Quality)
    A -->|Weight| C(Data Completeness)
    A -->|Weight| D(Source Reliability)
    B --> E{Final Score}
    C --> E
    D --> E
```

## Prompt Evolution & Optimization

### 1. Basic Prompt Structure

```python
BASIC_PROMPT = """
Analyze this medical text for:
1. Genetic variants
2. Clinical evidence
3. Molecular mechanisms
"""
```

### 2. ReACT Integration

```python
REACT_PROMPT = """
Use ReACT methodology to analyze:
1. REASON about evidence quality
2. ACT to extract structured data
3. CONCLUDE with confidence levels
4. THINK about validation
"""
```

### 3. Final Structured Prompt

```python
STRUCTURED_PROMPT = """
Provide JSON output with:
{
    "variants": [...],
    "evidence": [...],
    "molecular": [...],
    "confidence": {...}
}
Include ReACT reasoning in each section.
"""
```

## Validation Strategy

### Data Validation Flow

```mermaid
stateDiagram-v2
    [*] --> InputValidation
    InputValidation --> SchemaValidation
    SchemaValidation --> DataValidation
    DataValidation --> QualityCheck
    QualityCheck --> ConfidenceScoring
    ConfidenceScoring --> [*]
```

### Error Recovery Strategy

```mermaid
graph TD
    A[Error Detected] -->|Classify| B{Error Type}
    B -->|Schema| C[Fix Structure]
    B -->|Data| D[Clean Data]
    B -->|Quality| E[Flag Issue]
    C -->|Retry| F[Validate]
    D -->|Retry| F
    E -->|Log| G[Continue]
```
