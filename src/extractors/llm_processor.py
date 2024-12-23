from anthropic import Anthropic
import asyncio
from typing import Dict, Any, Optional
import logging
import os
import json
import re
from tqdm import tqdm
from ..utils.logger import setup_logger
from ..prompts.prompt_templates import PromptTemplates

class LLMProcessor:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-3-opus-20240229"
        self.prompt_templates = PromptTemplates()
        self.logger = setup_logger(__name__)
        self.logger.info("🤖 Initializing LLM Processor")
        
        # Configure retry parameters
        self.max_retries = 3
        self.base_delay = 1  # Base delay in seconds

    async def analyze_text(
        self,
        text: str,
        prompt: str,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """Analyze text using Claude with robust response handling and retries"""
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"📤 Sending request to Claude (attempt {attempt + 1})")
                self.logger.debug(f"Text length: {len(text)} characters")
                self.logger.debug(f"Prompt preview: {prompt[:100]}...")

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=[{
                        "role": "user",
                        "content": f"{prompt}\n\nText to analyze:\n{text}"
                    }]
                )
                
                self.logger.info("📥 Received response from Claude")
                return await self._process_response(response)
                
            except Exception as e:
                delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                self.logger.warning(
                    f"⚠️ Attempt {attempt + 1} failed: {str(e)}. "
                    f"Retrying in {delay} seconds..."
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(delay)
                else:
                    self.logger.error("❌ All retry attempts failed")
                    return self._create_fallback_response()

    async def _process_response(self, response: Any) -> Dict[str, Any]:
        """Process Claude response with enhanced validation"""
        try:
            self.logger.info("🔍 Processing Claude response")
            content = response.content[0].text
            self.logger.debug(f"Raw response preview: {content[:200]}...")
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                self.logger.info("Found JSON structure in response")
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    self.logger.warning("JSON parsing failed, falling back to text processing")
                    return await self._clean_and_structure_response(content)
            else:
                self.logger.info("No JSON found, processing as text")
                return await self._clean_and_structure_response(content)
                
        except Exception as e:
            self.logger.error(f"❌ Error processing response: {str(e)}", exc_info=True)
            return await self._clean_and_structure_response(content)

    async def _clean_and_structure_response(self, text: str) -> Dict[str, Any]:
        """Convert text response into structured format with validation"""
        self.logger.info("📝 Structuring text response")
        
        # Remove markdown formatting
        cleaned_text = text.replace("```json", "").replace("```", "").strip()
        
        # Initialize sections
        structured_data = {
            "variants": [],
            "clinical_evidence": [],
            "molecular_data": [],
            "raw_text": cleaned_text
        }
        
        # Parse text using ReACT approach
        current_section = None
        reasoning_block = []
        action_block = []
        conclusion_block = []
        
        self.logger.debug("Parsing text sections using ReACT methodology")
        for line in cleaned_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Identify ReACT blocks
            if "REASON" in line:
                current_section = "reasoning"
            elif "ACTION" in line:
                current_section = "action"
            elif "CONCLUDE" in line:
                current_section = "conclusion"
            elif current_section:
                # Add content to appropriate block
                if current_section == "reasoning":
                    reasoning_block.append(line)
                elif current_section == "action":
                    action_block.append(line)
                elif current_section == "conclusion":
                    conclusion_block.append(line)
            
            # Identify and categorize content
            if "variant" in line.lower() or "mutation" in line.lower():
                structured_data["variants"].append({
                    "description": line,
                    "reasoning": "\n".join(reasoning_block),
                    "action": "\n".join(action_block),
                    "conclusion": "\n".join(conclusion_block)
                })
            elif "clinical" in line.lower() or "evidence" in line.lower():
                structured_data["clinical_evidence"].append({
                    "description": line,
                    "reasoning": "\n".join(reasoning_block),
                    "action": "\n".join(action_block),
                    "conclusion": "\n".join(conclusion_block)
                })
            elif "molecular" in line.lower() or "pathway" in line.lower():
                structured_data["molecular_data"].append({
                    "description": line,
                    "reasoning": "\n".join(reasoning_block),
                    "action": "\n".join(action_block),
                    "conclusion": "\n".join(conclusion_block)
                })

        self.logger.info(
            f"✅ Structured response created with "
            f"{len(structured_data['variants'])} variants, "
            f"{len(structured_data['clinical_evidence'])} clinical items, and "
            f"{len(structured_data['molecular_data'])} molecular items"
        )

        return structured_data

    def _create_fallback_response(self) -> Dict[str, Any]:
        """Create a fallback response when analysis fails"""
        self.logger.warning("⚠️ Creating fallback response")
        return {
            "variants": [],
            "clinical_evidence": [],
            "molecular_data": [],
            "error": "Analysis failed",
            "raw_text": ""
        }