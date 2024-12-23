class PromptTemplates:
    VARIANT_ANALYSIS = '''Analyze this medical text and provide a comprehensive structured JSON output. Extract ALL variants mentioned, including those with uncertain significance. For each element provide:

{
  "variants": [
    {
      "name": "precise HGVS notation",
      "type": "mutation/fusion/amplification/etc",
      "prevalence": "frequency in population",
      "significance": "pathogenic/likely pathogenic/etc",
      "drugs": ["associated drugs"],
      "evidence_level": "A/B/C/D",
      "molecular_effect": "pathway impact",
      "clinical_relevance": "therapeutic implications",
      "resistance_mechanisms": ["known resistance pathways"],
      "biomarker_status": "predictive/prognostic/diagnostic",
      "references": ["supporting citations"]
    }
  ],
  "clinical_evidence": [
    {
      "type": "therapeutic/diagnostic/prognostic",
      "drugs": ["drug names"],
      "phase": "trial phase",
      "population": "patient characteristics",
      "line": "line of therapy",
      "evidence_level": "A/B/C/D",
      "outcome": "response/resistance/etc",
      "significance": "clinical importance",
      "confidence": 0-1 score,
      "supporting_data": ["key trial results", "statistics"],
      "biomarker_requirements": ["required biomarkers"]
    }
  ],
  "molecular_data": [
    {
      "pathway": "pathway name",
      "alterations": ["specific changes"],
      "interactions": {
        "upstream": ["pathways"],
        "downstream": ["pathways"]
      },
      "therapeutic_implications": ["drug targets", "resistance mechanisms"],
      "biomarker_relevance": "description",
      "evidence_strength": "high/moderate/low",
      "confidence": 0-1 score
    }
  ]
}

Be comprehensive and include ALL relevant information from the text. Provide evidence levels and confidence scores for each entry.'''