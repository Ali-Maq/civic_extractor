import asyncio
from pathlib import Path
import logging
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from tqdm import tqdm
from .extractors.pdf_processor import PDFProcessor
from .extractors.llm_processor import LLMProcessor
from .extractors.civic_extractor import CivicExtractor
from .utils.logger import setup_logger

class CivicExtractionPipeline:
    def __init__(self):
        load_dotenv()
        self.logger = setup_logger(__name__)
        self.logger.info("🚀 Initializing CIVIC Extraction Pipeline")
        
        # Initialize components with progress tracking
        with tqdm(total=3, desc="Initializing components") as pbar:
            self.pdf_processor = PDFProcessor()
            pbar.update(1)
            
            self.llm_processor = LLMProcessor()
            pbar.update(1)
            
            self.civic_extractor = CivicExtractor(self.llm_processor)
            pbar.update(1)
        
        self.logger.info("✅ Pipeline initialized successfully")

    async def process_paper(self, pdf_path: str, output_path: str = None) -> dict:
        """Process paper with enhanced progress tracking and validation"""
        try:
            start_time = datetime.now()
            self.logger.info(f"📄 Processing PDF: {pdf_path}")
            
            # Create overall progress bar
            overall_progress = tqdm(total=100, desc="Overall Progress", position=0)
            
            # Extract text from PDF
            self.logger.info("1️⃣ Extracting text from PDF")
            text = self.pdf_processor.extract_text(pdf_path)
            self.logger.info(f"📝 Extracted {len(text)} characters from PDF")
            overall_progress.update(20)
            
            # Extract CIVIC data
            self.logger.info("2️⃣ Analyzing text with CIVIC extractor")
            civic_data = await self.civic_extractor.extract_civic_data(text)
            overall_progress.update(60)
            
            # Generate output path if not provided
            if output_path is None:
                output_path = f"analysis_{Path(pdf_path).stem}.json"
            
            # Save results
            self.logger.info(f"3️⃣ Saving results to {output_path}")
            
            # Create results directory if it doesn't exist
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Calculate and log processing statistics
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Access model fields directly
            confidence_scores = civic_data.metadata.get('confidence_scores', {})
            
            stats = {
                "processing_time": processing_time,
                "text_length": len(text),
                "num_variants": len(civic_data.variants),
                "num_clinical_evidence": len(civic_data.clinical_evidence),
                "num_molecular_data": len(civic_data.molecular_data),
                "overall_confidence": confidence_scores.get('overall', 0.0)
            }
            
            # Convert to dictionary for JSON serialization
            output_data = {
                "variants": civic_data.variants,
                "clinical_evidence": civic_data.clinical_evidence,
                "molecular_data": civic_data.molecular_data,
                "metadata": civic_data.metadata,
                "stats": stats
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, default=str)
                
            overall_progress.update(20)
            
            self.logger.info("📊 Processing Statistics:")
            for key, value in stats.items():
                self.logger.info(f"  - {key}: {value}")
            
            overall_progress.close()
            return output_data

        except Exception as e:
            self.logger.error(f"❌ Pipeline failed: {str(e)}", exc_info=True)
            if 'overall_progress' in locals():
                overall_progress.close()
            raise

async def main():
    """Enhanced main function with better error handling and progress display"""
    try:
        # Print startup banner
        print("\n" + "="*60)
        print("🧬 CIVIC Extraction Pipeline 🧬".center(60))
        print("="*60 + "\n")
        
        # Get PDF path from command line or environment
        pdf_path = os.sys.argv[1] if len(os.sys.argv) > 1 else os.getenv("PDF_PATH", "paper.pdf")
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print(f"📄 Processing: {pdf_path}\n")
        
        # Initialize and run pipeline
        pipeline = CivicExtractionPipeline()
        result = await pipeline.process_paper(pdf_path)
        
        # Print results
        print("\n📊 Extraction Results:")
        print("="*60)
        try:
            # Format variants
            if result['variants']:
                print("\nVariants Found:", len(result['variants']))
                for variant in result['variants'][:5]:  # Show first 5 variants
                    print(f"- {variant.get('description', 'No description')}")
                if len(result['variants']) > 5:
                    print(f"... and {len(result['variants']) - 5} more")
                    
            # Format clinical evidence
            if result['clinical_evidence']:
                print("\nClinical Evidence Items:", len(result['clinical_evidence']))
                for evidence in result['clinical_evidence'][:5]:
                    print(f"- {evidence.get('description', 'No description')}")
                if len(result['clinical_evidence']) > 5:
                    print(f"... and {len(result['clinical_evidence']) - 5} more")
                    
            # Format molecular data
            if result['molecular_data']:
                print("\nMolecular Data Items:", len(result['molecular_data']))
                for data in result['molecular_data'][:5]:
                    print(f"- {data.get('description', 'No description')}")
                if len(result['molecular_data']) > 5:
                    print(f"... and {len(result['molecular_data']) - 5} more")
                    
            # Print statistics
            if result.get('stats'):
                print("\nProcessing Statistics:")
                for key, value in result['stats'].items():
                    print(f"  {key}: {value}")
                    
        except Exception as e:
            print("⚠️ Error formatting results:", str(e))
            print("Raw results:", result)
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())