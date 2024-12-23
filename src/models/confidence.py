from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class ConfidenceMetrics(BaseModel):
    """Enhanced metrics used for confidence scoring"""
    # Evidence-based metrics
    evidence_strength: float = Field(..., ge=0.0, le=1.0)
    evidence_consistency: float = Field(..., ge=0.0, le=1.0)
    evidence_quality: float = Field(..., ge=0.0, le=1.0)
    
    # Data quality metrics
    data_completeness: float = Field(..., ge=0.0, le=1.0)
    data_consistency: float = Field(..., ge=0.0, le=1.0)
    
    # Validation metrics
    extraction_confidence: float = Field(..., ge=0.0, le=1.0)
    validation_score: float = Field(..., ge=0.0, le=1.0)
    
    # ReACT-based metrics
    reasoning_confidence: float = Field(..., ge=0.0, le=1.0)
    action_confidence: float = Field(..., ge=0.0, le=1.0)
    conclusion_confidence: float = Field(..., ge=0.0, le=1.0)

class ConfidenceCalculator:
    """Enhanced confidence calculator with ReACT integration"""
    
    @staticmethod
    def calculate_score(metrics: ConfidenceMetrics) -> float:
        """Calculate weighted confidence score"""
        weights = {
            # Evidence weights
            'evidence_strength': 0.2,
            'evidence_consistency': 0.1,
            'evidence_quality': 0.1,
            
            # Data quality weights
            'data_completeness': 0.1,
            'data_consistency': 0.1,
            
            # Validation weights
            'extraction_confidence': 0.1,
            'validation_score': 0.1,
            
            # ReACT weights
            'reasoning_confidence': 0.1,
            'action_confidence': 0.1,
            'conclusion_confidence': 0.1
        }
        
        score = sum(
            getattr(metrics, metric) * weight 
            for metric, weight in weights.items()
        )
        
        return round(score, 3)

    @staticmethod
    def evaluate_evidence_metrics(evidence: Dict) -> Dict[str, float]:
        """Evaluate evidence-related confidence metrics"""
        metrics = {
            'evidence_strength': 0.0,
            'evidence_consistency': 0.0,
            'evidence_quality': 0.0
        }
        
        # Evidence strength
        if evidence.get('evidence_level') in ['A', 'B']:
            metrics['evidence_strength'] = 0.8
        elif evidence.get('evidence_level') == 'C':
            metrics['evidence_strength'] = 0.6
        elif evidence.get('evidence_level') == 'D':
            metrics['evidence_strength'] = 0.4
        else:
            metrics['evidence_strength'] = 0.2
            
        # Evidence consistency
        metrics['evidence_consistency'] = 0.8 if evidence.get('evidence_direction') == 'Supportive' else 0.4
        
        # Evidence quality
        has_citations = bool(evidence.get('citations'))
        has_validation = bool(evidence.get('validation'))
        metrics['evidence_quality'] = 0.8 if (has_citations and has_validation) else 0.4
        
        return metrics

    @staticmethod
    def evaluate_react_metrics(
        reasoning: bool = False,
        action: bool = False,
        conclusion: bool = False
    ) -> Dict[str, float]:
        """Evaluate ReACT-based confidence metrics"""
        return {
            'reasoning_confidence': 0.8 if reasoning else 0.2,
            'action_confidence': 0.8 if action else 0.2,
            'conclusion_confidence': 0.8 if conclusion else 0.2
        }

    @staticmethod
    def evaluate_validation_metrics(validation_result: Optional[Dict] = None) -> Dict[str, float]:
        """Evaluate validation-related confidence metrics"""
        if not validation_result:
            return {
                'extraction_confidence': 0.5,
                'validation_score': 0.5
            }
            
        return {
            'extraction_confidence': validation_result.get('confidence_score', 0.5),
            'validation_score': 0.8 if validation_result.get('is_valid', False) else 0.2
        }