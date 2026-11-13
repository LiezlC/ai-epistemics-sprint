"""OpenRouter chat-completions route for the Epistemics pilot (sprint code, written 13 Nov 2026).

PREEXISTING CODE REUSED UNCHANGED: `con-artist/providers.py` (Swarm Alignment Sprint work, 6 Nov 2026) is IMPORTED
as it is: Providers, Result, RetryableError, SpendCapReached, retry and back-off, concurrency limits, spend cap,
key scrubbing. It is not copied and not edited.

WHAT IS NEW HERE (the preexisting OpenRouter route uses the Responses endpoint and sends no temperature and no seed,
so it cannot give greedy, seeded runs):
  - a subclass `SprintProviders` that adds the route "openrouter_chat" (POST /chat/completions) with temperature,
    seed, and thinking switched off, and asks OpenRouter to report the cost;
  - everything else is delegated to the preexisting class.

The key comes from the environment variable OPENROUTER_API_KEY (injected by the Modal Secret `openrouter`); it is
never logged. Not yet run against the real API.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
# Where the preexisting providers.py lives: on the laptop it is <repo>/con-artist; on Modal it is shipped to CON_ARTIST_DIR.
_CA = os.environ.get("CON_ARTIST_DIR") or str(_HERE.parents[2] / "con-artist")
if _CA not in sys.path:
    sys.path.insert(0, _CA)

from providers import Providers, Result, RetryableError, SpendCapReached, scrub  # noqa: E402  (preexisting, unchanged)

CHAT_BASE = "https://openrouter.ai/api/v1"
KEY_ENV = "OPENROUTER_API_KEY"

# USD per 1M tokens, from OpenRouter's public model list fetched 13 Nov 2026 (input, output).
PRICES = {
    "qwen/qwen3.8-max-0902": (2.0, 6.0),
    "qwen/qwen3.8-27b": (0.15, 1.875),
}


class SprintProviders(Providers):
    def __init__(self, seed=20261113, thinking="off", **kw):
        limits = {**(kw.pop("limits", None) or {}), "openrouter_chat": 8}
        prices = {m: p[1] for m, p in PRICES.items()}
        prices_in = {m: p[0] for m, p in PRICES.items()}
        super().__init__(limits=limits, prices=kw.pop("prices", prices), prices_in=kw.pop("prices_in", prices_in), **kw)
        self.seed = seed
        self.thinking = thinking  # "off" or "default"

    async def _once(self, route, model, system, user, max_tokens, effort, temperature) -> Result:
        if route == "openrouter_chat":
            return await self._chat(model, system, user, max_tokens, temperature)
        return await super()._once(route, model, system, user, max_tokens, effort, temperature)

    async def _chat(self, model, system, user, max_tokens, temperature) -> Result:
        msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
        body = {"model": model, "messages": msgs, "max_tokens": max_tokens,
                "temperature": 0 if temperature is None else temperature, "seed": self.seed,
                "usage": {"include": True}}
        if self.thinking == "off":
            body["reasoning"] = {"enabled": False}
        d = await self._post(CHAT_BASE + "/chat/completions", body, {"Authorization": "Bearer " + os.environ[KEY_ENV]})
        ch = (d.get("choices") or [{}])[0]
        msg = ch.get("message") or {}
        u = d.get("usage") or {}
        det = u.get("completion_tokens_details") or {}
        cost = u.get("cost")
        return Result(text=msg.get("content") or "", tokens_in=u.get("prompt_tokens"), tokens_out=u.get("completion_tokens"),
                      reasoning_tokens=det.get("reasoning_tokens"), finish_reason=ch.get("finish_reason"),
                      model_served=d.get("model"), cost_usd=float(cost) if isinstance(cost, (int, float)) else 0.0)
