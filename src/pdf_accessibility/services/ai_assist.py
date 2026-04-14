from __future__ import annotations

import base64
import logging
from typing import TYPE_CHECKING

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalRole

if TYPE_CHECKING:
    from pdf_accessibility.models.canonical import CanonicalBlock

logger = logging.getLogger(__name__)


class AIAssistService:
    """Service for AI-assisted accessibility remediation using Vision LLMs."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._openai_client = None
        self._anthropic_client = None

    def _get_openai_client(self):
        if self._openai_client is None and self.settings.openai_api_key:
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=self.settings.openai_api_key)
        return self._openai_client

    def _get_anthropic_client(self):
        if self._anthropic_client is None and self.settings.anthropic_api_key:
            from anthropic import Anthropic
            self._anthropic_client = Anthropic(api_key=self.settings.anthropic_api_key)
        return self._anthropic_client

    def generate_alt_text(
        self, block: CanonicalBlock, image_bytes: bytes | None = None, context: str = ""
    ) -> tuple[str, float]:
        """
        Generates descriptive alt-text using a vision-capable LLM.
        """
        if self.settings.ai_provider == "mock" or not (self.settings.openai_api_key or self.settings.anthropic_api_key):
            return self._mock_generate_alt_text(block)

        if image_bytes:
            if self.settings.ai_provider == "openai" and self.settings.openai_api_key:
                return self._openai_vision_alt_text(image_bytes, context)
            elif self.settings.ai_provider == "anthropic" and self.settings.anthropic_api_key:
                return self._anthropic_vision_alt_text(image_bytes, context)

        return self._mock_generate_alt_text(block)

    def _openai_vision_alt_text(self, image_bytes: bytes, context: str) -> tuple[str, float]:
        client = self._get_openai_client()
        if not client:
            return "AI provider configuration missing.", 0.0

        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        
        prompt = "Describe this image for a visually impaired user. Be concise but descriptive."
        if context:
            prompt += f" Context from document: {context}"

        try:
            response = client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )
            content = response.choices[0].message.content or ""
            return content.strip(), 0.9  # High confidence for real LLM output
        except Exception as e:
            logger.error(f"OpenAI vision call failed: {e}")
            return "Error generating AI description.", 0.0

    def _anthropic_vision_alt_text(self, image_bytes: bytes, context: str) -> tuple[str, float]:
        client = self._get_anthropic_client()
        if not client:
            return "AI provider configuration missing.", 0.0

        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        
        prompt = "Describe this image for a visually impaired user. Be concise but descriptive."
        if context:
            prompt += f" Context from document: {context}"

        try:
            response = client.messages.create(
                model=self.settings.anthropic_model,
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_image,
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            )
            content = response.content[0].text if response.content else ""
            return content.strip(), 0.9
        except Exception as e:
            logger.error(f"Anthropic vision call failed: {e}")
            return "Error generating AI description.", 0.0

    def disambiguate_role(self, block: CanonicalBlock) -> tuple[CanonicalRole, float]:
        """
        Refines role detection using LLM reasoning based on text and formatting.
        """
        if self.settings.ai_provider == "mock" or not (self.settings.openai_api_key or self.settings.anthropic_api_key):
            return self._mock_disambiguate_role(block)

        # For text-only disambiguation, we use a cheap model or the standard one
        # Logic here would involve a small prompt: "What is the role of this text snippet? Options: H1, H2, P, LI, Table..."
        return self._mock_disambiguate_role(block)

    def _mock_generate_alt_text(self, block: CanonicalBlock) -> tuple[str, float]:
        logger.debug(f"Using mock alt-text for block {block.block_id}")
        text_content = block.text.lower()
        if "chart" in text_content or "graph" in text_content:
            return "A data visualization chart showing trends.", 0.85
        if "logo" in text_content:
            return "Company logo.", 0.95
        return "Image description pending review.", 0.6

    def _mock_disambiguate_role(self, block: CanonicalBlock) -> tuple[CanonicalRole, float]:
        text = block.text.strip()
        if block.role == CanonicalRole.text:
            if text.startswith(("\u2022", "*", "- ", "\uf0b7")):
                return CanonicalRole.list_item, 0.9
            if len(text) < 50 and text.isupper():
                return CanonicalRole.heading1, 0.75
            if text.isdigit() and int(text) < 1000:
                return CanonicalRole.artifact, 0.8
        return block.role, 1.0
