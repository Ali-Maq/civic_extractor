from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime

class ProcessingMetadata(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    source: str = ""
    text_length: int = 0
    processing_time: float = 0.0
    validation_status: str = "pending"
    confidence_scores: Dict[str, float] = Field(default_factory=dict)

class CivicExtraction(BaseModel):
    # Making fields more flexible to handle various response formats
    variants: List[Dict[str, Any]] = Field(default_factory=list)
    clinical_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    molecular_data: List[Dict[str, Any]] = Field(default_factory=list)
    raw_text: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_llm_response(cls, response_data: Dict[str, Any], text_length: int) -> 'CivicExtraction':
        """Create CivicExtraction from LLM response with safe parsing"""
        try:
            # Handle different possible response structures
            variants = []
            clinical_evidence = []
            molecular_data = []

            # Safe extraction helper
            def safe_extract(data: Any, key: str) -> List[Dict[str, Any]]:
                if not isinstance(data, dict):
                    return []
                extracted = data.get(key, [])
                if isinstance(extracted, dict):
                    return [extracted]
                elif isinstance(extracted, list):
                    return extracted
                return []

            # Try to extract from different possible structures
            if "Genetic Variants & Mutations" in response_data:
                variants = safe_extract(response_data["Genetic Variants & Mutations"], "variants")
            elif "variants" in response_data:
                variants = safe_extract(response_data, "variants")

            if "Clinical Evidence" in response_data:
                clinical_evidence = safe_extract(response_data["Clinical Evidence"], "evidence")
            elif "clinical_evidence" in response_data:
                clinical_evidence = safe_extract(response_data, "clinical_evidence")

            if "Molecular Mechanisms" in response_data:
                molecular_data = safe_extract(response_data["Molecular Mechanisms"], "data")
            elif "molecular_data" in response_data:
                molecular_data = safe_extract(response_data, "molecular_data")

            # Convert all values to strings for consistency
            def ensure_str_values(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
                return [{k: str(v) if not isinstance(v, (list, dict)) else v 
                        for k, v in item.items()} for item in items]

            return cls(
                variants=ensure_str_values(variants),
                clinical_evidence=ensure_str_values(clinical_evidence),
                molecular_data=ensure_str_values(molecular_data),
                raw_text=str(response_data),
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "source": "claude-3-opus-20240229",
                    "text_length": text_length,
                    "processing_time": 0.0,
                    "validation_status": "processed",
                    "confidence_scores": {"overall": 0.8}
                }
            )
        except Exception as e:
            # Fallback to a minimal valid structure
            return cls(
                variants=[{"description": "Extraction failed", "error": str(e)}],
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "source": "claude-3-opus-20240229",
                    "text_length": text_length,
                    "processing_time": 0.0,
                    "validation_status": "failed",
                    "confidence_scores": {"overall": 0.0}
                }
            )

    def model_dump_json(self, **kwargs):
        return super().model_dump_json(exclude_none=True)