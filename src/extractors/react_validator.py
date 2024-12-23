from typing import Dict, Any, List, Optional
from ..models.data_models import ValidationResult, CivicExtraction
from ..utils.logger import setup_logger
import logging

class ReactValidator:
    """ReACT-based validation for CIVIC extractions"""
    
    def __init__(self, llm_processor):
        self.llm_processor = llm_processor
        self.logger = setup_logger(__name__)

    async def validate_extraction(
        self, 
        extraction: Dict[str, Any],
        validation_type: str = "extraction"
    ) -> ValidationResult:
        """Validate extraction using ReACT methodology"""
        try:
            # Get appropriate validation prompt
            if validation_type == "extraction":
                prompt = self.llm_processor.prompt_templates.VALIDATION_PROMPT
            else:
                prompt = self.llm_processor.prompt_templates.POST_PROCESSING_PROMPT
            
            # Get validation from LLM
            validation_response = await self.llm_processor.analyze_text(
                text=str(extraction),
                prompt=prompt
            )
            
            # Parse validation response
            validation_result = ValidationResult(
                is_valid=validation_response.get('is_valid', False),
                confidence_score=validation_response.get('confidence_score', 0.0),
                reasoning=validation_response.get('reasoning', ''),
                suggestions=validation_response.get('suggestions', []),
                validation_type=validation_type
            )
            
            self.logger.info(
                f"✅ {validation_type.title()} validation completed "
                f"(confidence: {validation_result.confidence_score:.2f})"
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"❌ Validation failed: {str(e)}", exc_info=True)
            return ValidationResult(
                is_valid=False,
                confidence_score=0.0,
                reasoning=f"Validation failed: {str(e)}",
                suggestions=["Retry validation"],
                validation_type=validation_type
            )

    async def validate_full_extraction(
        self,
        extraction: CivicExtraction
    ) -> CivicExtraction:
        """Perform both extraction and post-processing validation"""
        try:
            # Validate each component
            for variant in extraction.variants:
                variant.validation = await self.validate_extraction(
                    variant.dict(),
                    "extraction"
                )
                
            for evidence in extraction.clinical_evidence:
                evidence.validation = await self.validate_extraction(
                    evidence.dict(),
                    "extraction"
                )
                
            for data in extraction.molecular_data:
                data.validation = await self.validate_extraction(
                    data.dict(),
                    "extraction"
                )
            
            # Perform post-processing validation
            post_validation = await self.validate_extraction(
                extraction.dict(),
                "post-processing"
            )
            
            # Update metadata
            extraction.metadata.validation_status = (
                "valid" if post_validation.is_valid else "invalid"
            )
            
            return extraction
            
        except Exception as e:
            self.logger.error(f"❌ Full validation failed: {str(e)}", exc_info=True)
            return extraction