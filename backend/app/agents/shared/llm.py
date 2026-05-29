import logging
import asyncio
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiLLMClientRotator:
    """
    Smart LLM client with sequential key rotation.
    - Tries keys in order (not random), so Key 1 is always preferred.
    - When a key gets a 429 (quota exhausted), it is marked as exhausted 
      and skipped for 60 seconds before being tried again.
    - This eliminates wasted retry wait time - if Key 1 is exhausted, 
      it instantly moves to Key 2, then Key 3, etc.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.2, **kwargs):
        self.model_name = model_name
        self.temperature = temperature

        available_keys = []
        for attr in ['google_api_key', 'google_api_key_2', 'google_api_key_3',
                     'google_api_key_4', 'google_api_key_5', 'google_api_key_6']:
            key = getattr(settings, attr, None)
            if key:
                available_keys.append(key)

        if not available_keys:
            raise ValueError("No GOOGLE_API_KEY environment variables are set.")

        logger.info(f"Loaded {len(available_keys)} API keys for sequential key rotation.")

        self.clients = []
        for key in available_keys:
            client = ChatGoogleGenerativeAI(
                model=self.model_name,
                api_key=key,
                temperature=self.temperature,
                max_tokens=8192,
                max_retries=0,
                **kwargs
            )
            self.clients.append(client)

        # Track when each key was last exhausted. key_index -> datetime
        self._exhausted_until: dict[int, datetime] = {}

    async def _get_next_client(self):
        """
        Returns the first non-exhausted client in order.
        If all are exhausted, waits for the soonest one to reset.
        """
        now = datetime.now()
        for i, client in enumerate(self.clients):
            exhausted_until = self._exhausted_until.get(i)
            if exhausted_until is None or now >= exhausted_until:
                logger.debug(f"Using API Key #{i+1}")
                return i, client

        # All keys exhausted — find the one that resets soonest
        soonest_idx = min(self._exhausted_until, key=lambda k: self._exhausted_until[k])
        soonest_time = self._exhausted_until[soonest_idx]
        wait_secs = max(0, (soonest_time - now).total_seconds())
        if wait_secs > 0:
            logger.warning(f"All API keys exhausted. Key #{soonest_idx+1} resets in {wait_secs:.0f}s. Sleeping...")
            await asyncio.sleep(wait_secs)
            
        return soonest_idx, self.clients[soonest_idx]

    def _mark_exhausted(self, idx: int, retry_delay_seconds: int = 60):
        """Mark a key as exhausted for retry_delay_seconds."""
        self._exhausted_until[idx] = datetime.now() + timedelta(seconds=retry_delay_seconds)
        logger.warning(f"API Key #{idx+1} marked exhausted for {retry_delay_seconds}s")

    async def ainvoke(self, messages: list[BaseMessage]) -> BaseMessage:
        """Invoke with smart key rotation — instantly switches on quota errors."""
        max_attempts = len(self.clients) * 3
        for attempt in range(max_attempts):
            idx, client = await self._get_next_client()
            try:
                response = await client.ainvoke(messages)
                return response
            except Exception as e:
                err = str(e)
                if "429" in err or "RESOURCE_EXHAUSTED" in err:
                    # Extract retry delay from error if available
                    import re
                    match = re.search(r'retry[_\s]in[:\s]+([\d.]+)s', err, re.IGNORECASE)
                    delay = int(float(match.group(1))) + 5 if match else 65
                    self._mark_exhausted(idx, delay)
                    logger.info(f"Key #{idx+1} quota hit. Rotating to next key instantly...")
                    continue
                logger.error(f"Non-quota error on Key #{idx+1}: {err[:120]}")
                raise
        raise RuntimeError("All API keys exhausted after maximum rotation attempts.")

    async def ainvoke_structured(self, messages: list[BaseMessage], schema: type[BaseModel]) -> BaseModel:
        """Invoke with structured output and smart key rotation."""
        max_attempts = len(self.clients) * 3
        for attempt in range(max_attempts):
            idx, client = await self._get_next_client()
            try:
                structured_client = client.with_structured_output(schema)
                response = await structured_client.ainvoke(messages)
                return response
            except Exception as e:
                err = str(e)
                if "429" in err or "RESOURCE_EXHAUSTED" in err:
                    import re
                    match = re.search(r'retry[_\s]in[:\s]+([\d.]+)s', err, re.IGNORECASE)
                    delay = int(float(match.group(1))) + 5 if match else 65
                    self._mark_exhausted(idx, delay)
                    logger.info(f"Key #{idx+1} quota hit. Rotating to next key instantly...")
                    continue
                logger.error(f"Non-quota error on Key #{idx+1}: {err[:120]}")
                raise
        raise RuntimeError("All API keys exhausted after maximum rotation attempts.")


# Singleton instance — shared across all agents
gemini_client = GeminiLLMClientRotator()
