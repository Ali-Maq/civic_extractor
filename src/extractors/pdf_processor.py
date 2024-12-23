from PyPDF2 import PdfReader
from pathlib import Path
import logging
from typing import Optional

class PDFProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            self.logger.info(f"Successfully extracted text from {pdf_path}")
            return text
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def extract_metadata(self, pdf_path: str) -> dict:
        """Extract PDF metadata"""
        try:
            reader = PdfReader(pdf_path)
            metadata = reader.metadata
            return {
                "title": metadata.get("/Title", ""),
                "author": metadata.get("/Author", ""),
                "subject": metadata.get("/Subject", ""),
                "keywords": metadata.get("/Keywords", ""),
                "creator": metadata.get("/Creator", ""),
                "producer": metadata.get("/Producer", ""),
                "creation_date": metadata.get("/CreationDate", "")
            }
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {str(e)}")
            return {}