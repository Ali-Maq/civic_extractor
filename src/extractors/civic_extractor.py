from typing import Dict, Any, List
import logging
from datetime import datetime
from tqdm import tqdm
from ..models.data_models import CivicExtraction
from ..utils.logger import setup_logger

class CivicExtractor:
    def __init__(self, llm_processor):
        self.llm_processor = llm_processor
        self.logger = setup_logger(__name__)
        self.logger.info("🧬 Initializing CIVIC Extractor")

    def _clean_variant_data(self, variant: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced variant data cleaning"""
        return {
            "description": variant.get("name", ""),
            "variant_type": variant.get("type", ""),
            "significance": variant.get("significance", ""),
            "frequency": variant.get("prevalence", "unknown"),  # Added
            "drugs": variant.get("drugs", []),
            "evidence_level": variant.get("evidence_level", ""),
            "molecular_effect": variant.get("molecular_effect", ""),
            "clinical_relevance": variant.get("clinical_relevance", ""),
            "resistance_mechanisms": variant.get("resistance_mechanisms", []),  # Added
            "biomarker_status": variant.get("biomarker_status", ""),  # Added
            "confidence": self._calculate_confidence(variant),
            "citations": variant.get("references", [])  # Added
        }

    def _clean_clinical_evidence(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced clinical evidence cleaning"""
        return {
            "description": f"{evidence.get('type', '')}: {evidence.get('outcome', '')}",
            "evidence_type": evidence.get("type", ""),
            "drugs": evidence.get("drugs", []),
            "trial_phase": evidence.get("phase", ""),  # Added
            "patient_population": evidence.get("population", ""),  # Added
            "line_of_therapy": evidence.get("line", ""),  # Added
            "significance": evidence.get("significance", ""),
            "confidence": evidence.get("confidence", 0.0),
            "supporting_data": evidence.get("supporting_data", []),
            "biomarker_requirements": evidence.get("biomarker_requirements", [])  # Added
        }

    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Enhanced confidence calculation"""
        score = 0.0
        required_fields = [
            "name", "type", "significance", "evidence_level", 
            "molecular_effect", "clinical_relevance"
        ]
        
        # Check completeness
        completeness = sum(1 for field in required_fields if data.get(field)) / len(required_fields)
        
        # Evidence level weighting
        evidence_weights = {
            "A": 1.0,  # Multiple high-quality trials
            "B": 0.8,  # Single high-quality trial
            "C": 0.6,  # Multiple lower-quality studies
            "D": 0.4   # Case reports or expert opinion
        }
        evidence_score = evidence_weights.get(data.get("evidence_level", "").upper(), 0.2)
        
        # Supporting data weight
        supporting_data = len(data.get("supporting_data", []))
        support_score = min(1.0, supporting_data / 3)  # Normalize to max of 1.0
        
        # Calculate weighted score
        score = (completeness * 0.3) + (evidence_score * 0.5) + (support_score * 0.2)
        return round(min(1.0, score), 2)





    def _clean_molecular_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and standardize molecular data"""
        return {
            "description": f"Pathway: {data.get('pathway', '')}",
            "pathway": data.get("pathway", ""),
            "alterations": data.get("alterations", []),
            "interactions": data.get("interactions", []),
            "therapeutic_implications": data.get("therapeutic_implications", []),
            "confidence": data.get("confidence", 0.0)
        }

    async def extract_civic_data(self, text: str) -> CivicExtraction:
        """Extract CIVIC data with improved structure and validation"""
        try:
            start_time = datetime.now()
            self.logger.info("🔍 Starting CIVIC data extraction")
            
            # Initialize progress bar
            progress = tqdm(total=5, desc="Extracting CIVIC data")
            
            # Get analysis from LLM
            self.logger.info("🤖 Sending text to LLM for analysis")
            analysis = await self.llm_processor.analyze_text(
                text=text,
                prompt=self.llm_processor.prompt_templates.VARIANT_ANALYSIS
            )
            progress.update(1)
            
            # Process variants with better structure
            variants = [
                self._clean_variant_data(variant) 
                for variant in analysis.get('variants', [])
            ]
            progress.update(1)
            
            # Process clinical evidence
            clinical_evidence = [
                self._clean_clinical_evidence(evidence) 
                for evidence in analysis.get('clinical_evidence', [])
            ]
            progress.update(1)
            
            # Process molecular data
            molecular_data = [
                self._clean_molecular_data(data) 
                for data in analysis.get('molecular_data', [])
            ]
            progress.update(1)
            
            # Calculate confidence scores
            confidence_scores = {
                "variants": sum(v["confidence"] for v in variants) / len(variants) if variants else 0.0,
                "clinical": sum(e["confidence"] for e in clinical_evidence) / len(clinical_evidence) if clinical_evidence else 0.0,
                "molecular": sum(m["confidence"] for m in molecular_data) / len(molecular_data) if molecular_data else 0.0
            }
            confidence_scores["overall"] = sum(confidence_scores.values()) / len(confidence_scores)
            
            # Create extraction object
            extraction = CivicExtraction(
                variants=variants,
                clinical_evidence=clinical_evidence,
                molecular_data=molecular_data,
                raw_text=text,
                metadata={
                    "timestamp": str(datetime.now()),
                    "source": "claude-3-opus-20240229",
                    "text_length": len(text),
                    "processing_time": (datetime.now() - start_time).total_seconds(),
                    "validation_status": "processed",
                    "confidence_scores": confidence_scores
                }
            )
            progress.update(1)
            
            self.logger.info(f"✅ Extraction completed successfully")
            progress.close()
            
            return extraction

        except Exception as e:
            self.logger.error(f"❌ Extraction failed: {str(e)}", exc_info=True)
            if 'progress' in locals():
                progress.close()
            return CivicExtraction(
                metadata={
                    "timestamp": str(datetime.now()),
                    "source": "claude-3-opus-20240229",
                    "text_length": len(text),
                    "processing_time": 0.0,
                    "validation_status": "failed",
                    "confidence_scores": {"overall": 0.0}
                }
            )