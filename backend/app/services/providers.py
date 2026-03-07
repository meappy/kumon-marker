"""Vision AI provider abstraction for worksheet analysis.

Supports multiple providers with a common interface:
- anthropic: Anthropic API (supports both API keys and OAuth session tokens)
- gemini: Google Gemini API
- ollama: Local Ollama LLM
- openai: OpenAI API

Inspired by the provider patterns in macrosee, oh-my-opencode, and opencode-swarm.
"""

import base64
import json
import re
from abc import ABC, abstractmethod

from app.core.config import get_effective_setting


class VisionProvider(ABC):
    """Base class for AI vision providers."""

    @abstractmethod
    def analyse_image(self, image_bytes: bytes, prompt: str) -> str:
        """Send an image + prompt to the vision model. Returns raw text response."""
        ...

    @abstractmethod
    def text_query(self, prompt: str) -> str:
        """Send a text-only prompt. Returns raw text response."""
        ...


def parse_json_response(text: str) -> dict:
    """Extract JSON from a vision model response, handling markdown code blocks."""
    text = text.strip()
    if "```" in text:
        match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', text, re.DOTALL)
        if match:
            text = match.group(1)
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        return json.loads(match.group())
    raise ValueError("No valid JSON found in response")


# ---------------------------------------------------------------------------
# Anthropic provider (API key + OAuth session token support)
# ---------------------------------------------------------------------------

def _get_anthropic_client():
    """Create an Anthropic client, handling both API keys and OAuth tokens.

    OAuth tokens (starting with 'sk-ant-oat01-') use Bearer auth with
    the anthropic-beta header. Standard API keys use X-Api-Key auth.
    """
    import anthropic

    key = get_effective_setting("anthropic_api_key", "")
    extra_headers = {}

    if key.startswith("sk-ant-oat01-"):
        # OAuth token — use Bearer header + anthropic-beta flag
        client = anthropic.Anthropic(auth_token=key)
        client.api_key = None  # Prevent SDK sending X-Api-Key alongside Bearer
        extra_headers["anthropic-beta"] = "oauth-2025-04-20"
    else:
        client = anthropic.Anthropic(api_key=key)

    return client, extra_headers


class AnthropicProvider(VisionProvider):
    """Anthropic Claude vision provider.

    Supports both standard API keys (sk-ant-api...) and OAuth session
    tokens (sk-ant-oat01-...) for authenticated requests.
    """

    def analyse_image(self, image_bytes: bytes, prompt: str) -> str:
        model = get_effective_setting("anthropic_model", "claude-sonnet-4-20250514")
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        client, extra_headers = _get_anthropic_client()
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            extra_headers=extra_headers,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }],
        )
        return response.content[0].text.strip()

    def text_query(self, prompt: str) -> str:
        model = get_effective_setting("anthropic_model", "claude-sonnet-4-20250514")

        client, extra_headers = _get_anthropic_client()
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            extra_headers=extra_headers,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()


# ---------------------------------------------------------------------------
# Gemini provider (google-genai SDK)
# ---------------------------------------------------------------------------

class GeminiProvider(VisionProvider):
    """Google Gemini vision provider using the google-genai SDK."""

    def _get_client(self):
        from google import genai

        api_key = get_effective_setting("gemini_api_key", "")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not configured")
        return genai.Client(api_key=api_key)

    def analyse_image(self, image_bytes: bytes, prompt: str) -> str:
        from PIL import Image
        from io import BytesIO

        model = get_effective_setting("gemini_model", "gemini-2.0-flash")
        client = self._get_client()
        image = Image.open(BytesIO(image_bytes))
        response = client.models.generate_content(
            model=model,
            contents=[prompt, image],
        )
        return response.text.strip()

    def text_query(self, prompt: str) -> str:
        model = get_effective_setting("gemini_model", "gemini-2.0-flash")
        client = self._get_client()
        response = client.models.generate_content(
            model=model,
            contents=[prompt],
        )
        return response.text.strip()


# ---------------------------------------------------------------------------
# Ollama provider (local LLM)
# ---------------------------------------------------------------------------

class OllamaProvider(VisionProvider):
    """Ollama local LLM provider. No rate limits, no API keys."""

    def analyse_image(self, image_bytes: bytes, prompt: str) -> str:
        import httpx

        base_url = get_effective_setting("ollama_base_url", "http://localhost:11434")
        model = get_effective_setting("ollama_model", "moondream")
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "images": [image_b64],
                    "stream": False,
                },
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()

    def text_query(self, prompt: str) -> str:
        import httpx

        base_url = get_effective_setting("ollama_base_url", "http://localhost:11434")
        model = get_effective_setting("ollama_model", "moondream")

        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()


# ---------------------------------------------------------------------------
# OpenAI provider
# ---------------------------------------------------------------------------

class OpenAIProvider(VisionProvider):
    """OpenAI vision provider (GPT-4o, etc.)."""

    def _get_client(self):
        import openai

        api_key = get_effective_setting("openai_api_key", "")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not configured")
        return openai.OpenAI(api_key=api_key)

    def analyse_image(self, image_bytes: bytes, prompt: str) -> str:
        model = get_effective_setting("openai_model", "gpt-4o")
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        client = self._get_client()
        response = client.chat.completions.create(
            model=model,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}",
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }],
        )
        return response.choices[0].message.content.strip()

    def text_query(self, prompt: str) -> str:
        model = get_effective_setting("openai_model", "gpt-4o")

        client = self._get_client()
        response = client.chat.completions.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# Provider factory
# ---------------------------------------------------------------------------

PROVIDERS = {
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
    "ollama": OllamaProvider,
    "openai": OpenAIProvider,
}


def get_provider(provider_name: str | None = None) -> VisionProvider:
    """Get a vision provider instance by name.

    Falls back to the configured default (vision_provider setting).
    """
    if provider_name is None:
        provider_name = get_effective_setting("vision_provider", "ollama")

    cls = PROVIDERS.get(provider_name)
    if cls is None:
        raise ValueError(
            f"Unknown provider '{provider_name}'. "
            f"Available: {', '.join(PROVIDERS.keys())}"
        )
    return cls()


def get_validation_provider() -> VisionProvider:
    """Get the provider used for worksheet validation (sheet ID extraction).

    Uses validation_provider if set, otherwise falls back to the main
    vision_provider.
    """
    provider_name = get_effective_setting("validation_provider", "")
    if not provider_name:
        provider_name = get_effective_setting("vision_provider", "ollama")
    return get_provider(provider_name)
