"""
Cloudflare AI Vision caller.
Uses the @cf/llava-1.5-7b-hf model for vision + text extraction.
Falls back to Anthropic Claude if CF_ACCOUNT_ID is not set.
"""
import json
import os
import re
from .prompts import get_prompt
from .schemas import ExtractionMode, ExtractionResult

CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID", "")
CF_API_TOKEN = os.getenv("CF_API_TOKEN", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

CF_MODEL = "@cf/llava-1.5-7b-hf"
ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"


async def _call_cloudflare(image_b64: str, content_type: str, prompt: str) -> str:
    import httpx
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{CF_MODEL}"
    payload = {
        "image": list(bytes(image_b64, "utf-8")),  # CF AI expects byte array
        "prompt": prompt,
        "max_tokens": 1024,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            url,
            headers={"Authorization": f"Bearer {CF_API_TOKEN}"},
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("result", {}).get("description", "")


async def _call_anthropic(image_b64: str, content_type: str, prompt: str) -> str:
    import httpx
    payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": content_type,
                            "data": image_b64,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]


def _parse_json(text: str) -> dict:
    """Extract JSON from model output (strips markdown fences if present)."""
    # Remove markdown code blocks
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("```").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try extracting the first JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"raw_text": text, "parse_error": "Could not extract structured JSON"}


async def extract_from_image(
    image_b64: str,
    content_type: str,
    mode: ExtractionMode,
    filename: str,
) -> ExtractionResult:
    prompt = get_prompt(mode.value)

    if CF_ACCOUNT_ID and CF_API_TOKEN:
        raw_text = await _call_cloudflare(image_b64, content_type, prompt)
        model_used = CF_MODEL
    elif ANTHROPIC_API_KEY:
        raw_text = await _call_anthropic(image_b64, content_type, prompt)
        model_used = ANTHROPIC_MODEL
    else:
        raise RuntimeError(
            "No AI provider configured. Set CF_ACCOUNT_ID + CF_API_TOKEN or ANTHROPIC_API_KEY."
        )

    structured = _parse_json(raw_text)

    return ExtractionResult(
        mode=mode,
        filename=filename,
        raw_text=raw_text,
        structured=structured,
        model_used=model_used,
    )
