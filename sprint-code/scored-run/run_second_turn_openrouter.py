"""Run the second-turn conversations on an OpenRouter model (sprint code, 13 Nov 2026). Raw outputs only; no scoring.

The preexisting providers.py has no multi-turn route. This adds one WITHOUT editing it: a subclass of the headroom pilot's
SprintProviders with the route `openrouter_chat_multi`, whose `user` argument is the JSON-encoded chat (list of messages).
Frozen settings: temperature 0, seed 20261113, thinking off, max 200 tokens, parse = first JSON object (run_pilot.parse, unchanged).
Only rows whose first_arm equals --arm are run (the model's own first answer is in the conversation).

  python -I run_second_turn_openrouter.py --rows second_turn_rows.jsonl --arm 27b --model qwen/qwen3.8-27b --out RUN_DIR
Prints only counts. Key: OPENROUTER_API_KEY (or run inside Modal with modal_second_turn.py).
"""
import argparse
import asyncio
import hashlib
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pilot"))
import pilot_providers as pp  # noqa: E402  (sprint code; imports the preexisting providers.py unchanged)
import run_pilot as rp  # noqa: E402  (frozen parse rule, unchanged)

ROUTE = "openrouter_chat_multi"


class MultiTurnProviders(pp.SprintProviders):
    def __init__(self, **kw):
        super().__init__(limits={ROUTE: 8}, **kw)

    async def _once(self, route, model, system, user, max_tokens, effort, temperature):
        if route == ROUTE and not self.fake:
            return await self._chat_messages(model, json.loads(user), max_tokens, temperature)
        if route == ROUTE:  # test double: the preexisting base class only runs a fake under the route name "fake"
            return await pp.Providers._once(self, "fake", model, system, user, max_tokens, effort, temperature)
        return await super()._once(route, model, system, user, max_tokens, effort, temperature)

    async def _chat_messages(self, model, msgs, max_tokens, temperature):
        body = {"model": model, "messages": msgs, "max_tokens": max_tokens, "temperature": 0 if temperature is None else temperature,
                "seed": self.seed, "usage": {"include": True}}
        if self.thinking == "off":
            body["reasoning"] = {"enabled": False}
        d = await self._post(pp.CHAT_BASE + "/chat/completions", body, {"Authorization": "Bearer " + os.environ[pp.KEY_ENV]})
        ch = (d.get("choices") or [{}])[0]
        u = d.get("usage") or {}
        det = u.get("completion_tokens_details") or {}
        cost = u.get("cost")
        return pp.Result(text=(ch.get("message") or {}).get("content") or "", tokens_in=u.get("prompt_tokens"),
                         tokens_out=u.get("completion_tokens"), reasoning_tokens=det.get("reasoning_tokens"),
                         finish_reason=ch.get("finish_reason"), model_served=d.get("model"),
                         cost_usd=float(cost) if isinstance(cost, (int, float)) else 0.0)


async def run(a, rows, fake=None):
    prov = MultiTurnProviders(seed=a.seed, thinking=a.thinking, fake=fake, spend_cap=a.spend_cap)
    os.makedirs(a.out, exist_ok=True)

    async def one(r):
        meta = {k: r[k] for k in r if k not in ("messages",)}
        try:
            res = await prov.call(ROUTE, a.model, None, json.dumps(r["messages"]), a.max_tokens, temperature=0)
        except pp.SpendCapReached as e:
            return {**meta, "error": "spend cap: " + str(e)}
        parsed = rp.parse(res.text)
        meta.update({"answer2": res.text, "parsed": parsed is not None, "verdict": parsed[0] if parsed else None,
                     "roots": parsed[1] if parsed else None, "tokens_in": res.tokens_in, "tokens_out": res.tokens_out,
                     "reasoning_tokens": res.reasoning_tokens, "cost_usd": res.cost_usd, "error": res.error,
                     "model_served": res.model_served})
        return meta

    results = await asyncio.gather(*[one(r) for r in rows])
    with open(os.path.join(a.out, "second_turn_results.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for x in results:
            f.write(json.dumps(x) + "\n")
    return prov, results


def main(argv=None, fake=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--arm", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--spend-cap", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=200)
    ap.add_argument("--thinking", default="off", choices=["off", "default"])
    ap.add_argument("--seed", type=int, default=20261113)
    a = ap.parse_args(argv)
    rows = [json.loads(l) for l in open(a.rows, encoding="utf-8") if l.strip()]
    rows = [r for r in rows if r["first_arm"] == a.arm]
    prov, results = asyncio.run(run(a, rows, fake))
    summ = {"model": a.model, "arm": a.arm, "rows_sha256": hashlib.sha256(open(a.rows, "rb").read()).hexdigest(), "calls": prov.calls,
            "spend_usd": round(prov.spend, 5), "errors": sum(1 for x in results if x.get("error")),
            "unparseable": sum(1 for x in results if not x.get("error") and not x.get("parsed")),
            "reasoning_tokens_total": sum(x.get("reasoning_tokens") or 0 for x in results)}
    json.dump(summ, open(os.path.join(a.out, "run_summary_second_turn.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(summ, indent=1))
    d = {}
    for x in results:
        d.setdefault(x["branch"], Counter())[x.get("verdict") or "unparseable_or_error"] += 1
    for k, v in sorted(d.items()):
        print(f"{k:11} {dict(v)}")


if __name__ == "__main__":
    main()
