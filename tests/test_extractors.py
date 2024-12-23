import unittest
from pathlib import Path
import asyncio
from src.extractors.civic_extractor import CivicExtractor
from src.extractors.pdf_processor import PDFProcessor
from src.extractors.llm_processor import LLMProcessor

class TestExtractors(unittest.TestCase):
    def setUp(self):
        self.pdf_processor = PDFProcessor()
        self.llm_processor = LLMProcessor()
        self.civic_extractor = CivicExtractor(self.llm_processor)
        
    def test_pdf_extraction(self):
        pdf_path = Path("tests/data/test.pdf")
        text = self.pdf_processor.extract_text(str(pdf_path))
        self.assertIsNotNone(text)
        self.assertTrue(len(text) > 0)
        
    async def test_llm_processing(self):
        text = "Sample medical text"
        result = await self.llm_processor.analyze_text(text, "Test prompt")
        self.assertIsInstance(result, dict)
        
    async def test_civic_extraction(self):
        text = "Sample medical text with variants"
        result = await self.civic_extractor.extract_civic_data(text)
        self.assertTrue(hasattr(result, 'variants'))
        self.assertTrue(hasattr(result, 'clinical_evidence'))

if __name__ == '__main__':
    unittest.main()