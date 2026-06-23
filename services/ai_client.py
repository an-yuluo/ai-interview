"""DeepSeek API client with streaming support, retry logic, and fault tolerance."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncIterator

import httpx

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

logger = logging.getLogger(__name__)

_MAX_RETRIES = 2
_RETRY_DELAY = 2.0  # seconds


async def chat_completion(
    messages: list[dict],
    *,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    response_format: dict | None = None,
) -> str:
    """Non-streaming chat completion with retry. Returns full text."""
    payload: dict = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if response_format:
        payload["response_format"] = response_format

    for attempt in range(_MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
                    headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
                    json=payload,
                )
                if resp.status_code == 429:
                    # Rate limited — wait and retry
                    wait = float(resp.headers.get("Retry-After", _RETRY_DELAY * (attempt + 1)))
                    logger.warning(f"Rate limited (429), waiting {wait}s before retry")
                    await asyncio.sleep(wait)
                    continue
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            if attempt < _MAX_RETRIES:
                logger.warning(f"Connection error (attempt {attempt + 1}): {e}, retrying in {_RETRY_DELAY}s")
                await asyncio.sleep(_RETRY_DELAY)
            else:
                logger.error(f"Connection failed after {_MAX_RETRIES + 1} attempts: {e}")
                raise
        except httpx.HTTPStatusError:
            raise

    return "抱歉，AI 服务暂时不可用，请稍后重试。"


async def stream_chat_completion(
    messages: list[dict],
    *,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> AsyncIterator[str]:
    """Streaming chat completion with retry. Yields text chunks."""
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }

    for attempt in range(_MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream(
                    "POST",
                    f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
                    headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
                    json=payload,
                ) as resp:
                    if resp.status_code == 429:
                        wait = float(resp.headers.get("Retry-After", _RETRY_DELAY * (attempt + 1)))
                        logger.warning(f"Rate limited (429), waiting {wait}s before retry")
                        await asyncio.sleep(wait)
                        continue
                    if resp.status_code >= 500:
                        if attempt < _MAX_RETRIES:
                            logger.warning(f"Server error {resp.status_code}, retrying in {_RETRY_DELAY}s")
                            await asyncio.sleep(_RETRY_DELAY)
                            continue
                        yield "抱歉，AI 服务暂时繁忙，请稍后重试。"
                        return
                    resp.raise_for_status()

                    async for line in resp.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
            # If we get here, stream completed successfully
            return

        except (httpx.TimeoutException, httpx.ConnectError) as e:
            if attempt < _MAX_RETRIES:
                logger.warning(f"Stream connection error (attempt {attempt + 1}): {e}, retrying")
                await asyncio.sleep(_RETRY_DELAY)
            else:
                logger.error(f"Stream failed after {_MAX_RETRIES + 1} attempts: {e}")
                yield "网络连接中断，请检查网络后重试。"
                return

    # Fallback if all retries exhausted
    yield "抱歉，AI 服务暂时不可用，请稍后重试。"


async def chat_completion_json(
    messages: list[dict],
    *,
    temperature: float = 0.3,
) -> dict:
    """Chat completion expecting JSON response. Parses and returns dict."""
    text = await chat_completion(
        messages,
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    # Strip markdown code fences if present
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)
