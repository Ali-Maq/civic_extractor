from typing import Dict, Any, List, Optional
from ..models.data_models import (
    CivicExtraction, VariantData, ClinicalEvidence, 
    MolecularData, ValidationResult
)
from ..utils.logger import setup_logger

class DataValidator:
    """Enhanced validator with ReACT integration"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        
        # Define validation rules
        self.variant_rules = {
            "required_fields": [
                "description",
                "variant_type",
                "significance"
            ],
            "field_types": {
                "description": str,
                "variant_type": str,
                "significance": str,
                "confidence": float,
                "diseases": list,
                "drugs": list
            }
        }
        
        self.clinical_rules = {
            "required_fields": [
                "description",
                "evidence_type",
                "significance"
            ],
            "field_types": {
                "description": str,
                "evidence_type": str,
                "significance": str,
                "confidence": float,
                "citations": list
            }
        }
        
        self.molecular_rules = {
            "required_fields": [
                "description",
                "pathway",
                "mechanism"
            ],
            "field_types": {
                "description": str,
                "pathway": str,
                "mechanism": str,
                "confidence": float,
                "protein_changes": list,
                "cellular_effects": list
            }
        }

    def validate_extraction(self, extraction: CivicExtraction) -> ValidationResult:
        """Validate complete extraction"""
        try:
            # Initialize validation results
            is_valid = True
            validation_messages = []
            
            # Validate variants
            for variant in extraction.variants:
                variant_valid, messages = self._validate_variant(variant)
                is_valid &= variant_valid
                validation_messages.extend(messages)
            
            # Validate clinical evidence
            for evidence in extraction.clinical_evidence:
                evidence_valid, messages = self._validate_clinical(evidence)
                is_valid &= evidence_valid
                validation_messages.extend(messages)
            
            # Validate molecular data
            for data in extraction.molecular_data:
                data_valid, messages = self._validate_molecular(data)
                is_valid &= data_valid
                validation_messages.extend(messages)
            
            # Create validation result
            result = ValidationResult(
                is_valid=is_valid,
                confidence_score=self._calculate_validation_confidence(
                    extraction, validation_messages
                ),
                reasoning="\n".join(validation_messages),
                suggestions=self._generate_suggestions(validation_messages),
                validation_type="data_validation"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Validation failed: {str(e)}", exc_info=True)
            return ValidationResult(
                is_valid=False,
                confidence_score=0.0,
                reasoning=f"Validation error: {str(e)}",
                suggestions=["Check data structure"],
                validation_type="data_validation"
            )

    def _validate_variant(self, variant: VariantData) -> tuple[bool, List[str]]:
        """Validate variant data"""
        is_valid = True
        messages = []
        
        # Check required fields
        for field in self.variant_rules["required_fields"]:
            if not getattr(variant, field, None):
                is_valid = False
                messages.append(f"Missing required field: {field}")
        
        # Check field types
        for field, expected_type in self.variant_rules["field_types"].items():
            value = getattr(variant, field, None)
            if value is not None and not isinstance(value, expected_type):
                is_valid = False
                messages.append(
                    f"Invalid type for {field}: "
                    f"expected {expected_type}, got {type(value)}"
                )
        
        return is_valid, messages

    def _validate_clinical(self, evidence: ClinicalEvidence) -> tuple[bool, List[str]]:
        """Validate clinical evidence"""
        is_valid = True
        messages = []
        
        # Check required fields
        for field in self.clinical_rules["required_fields"]:
            if not getattr(evidence, field, None):
                is_valid = False
                messages.append(f"Missing required field: {field}")
        
        # Check field types
        for field, expected_type in self.clinical_rules["field_types"].items():
            value = getattr(evidence, field, None)
            if value is not None and not isinstance(value, expected_type):
                is_valid = False
                messages.append(
                    f"Invalid type for {field}: "
                    f"expected {expected_type}, got {type(value)}"
                )
        
        return is_valid, messages

    def _validate_molecular(self, data: MolecularData) -> tuple[bool, List[str]]:
        """Validate molecular data"""
        is_valid = True
        messages = []
        
        # Check required fields
        for field in self.molecular_rules["required_fields"]:
            if not getattr(data, field, None):
                is_valid = False
                messages.append(f"Missing required field: {field}")
        
        # Check field types
        for field, expected_type in self.molecular_rules["field_types"].items():
            value = getattr(data, field, None)
            if value is not None and not isinstance(value, expected_type):
                is_valid = False
                messages.append(
                    f"Invalid type for {field}: "
                    f"expected {expected_type}, got {type(value)}"
                )
        
        return is_valid, messages

    def _calculate_validation_confidence(
        self, 
        extraction: CivicExtraction,
        messages: List[str]
    ) -> float:
        """Calculate validation confidence score"""
        # Base confidence
        confidence = 1.0
        
        # Reduce confidence based on validation messages
        confidence -= len(messages) * 0.1
        
        # Check data completeness
        total_fields = len(self.variant_rules["required_fields"]) + \
                      len(self.clinical_rules["required_fields"]) + \
                      len(self.molecular_rules["required_fields"])
                      
        filled_fields = sum(
            1 for field in extraction.dict(exclude_none=True).keys()
            if field != "raw_text" and field != "metadata"
        )
        
        completeness = filled_fields / total_fields
        confidence *= completeness
        
        return max(0.0, min(1.0, confidence))

    def _generate_suggestions(self, messages: List[str]) -> List[str]:
        """Generate improvement suggestions based on validation messages"""
        suggestions = []
        
        # Group messages by type
        missing_fields = [msg for msg in messages if "Missing" in msg]
        invalid_types = [msg for msg in messages if "Invalid type" in msg]
        
        # Generate suggestions
        if missing_fields:
            suggestions.append(
                "Add missing required fields: " + 
                ", ".join(msg.split(": ")[1] for msg in missing_fields)
            )
            
        if invalid_types:
            suggestions.append(
                "Fix data types for: " +
                ", ".join(msg.split(":")[0].split(" ")[-1] for msg in invalid_types)
            )
            
        return suggestions or ["No improvements needed"]