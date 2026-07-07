# Spend guardrails for the Vercel AI SDK

> When you give an AI SDK agent a tool that spends money, nothing stands between
> the model and your card except the prompt. [sipi.bot](https://sipi.bot) is one
> `fetch` that returns `APPROVED`, `BLOCKED`, or `FLAGGED` (needs human approval)
> before the spend happens.

Tested live against `https://sipi.bot` with Node 18+ (global `fetch`). Works in
Node and edge runtimes. Client: `sipiGuard.ts` (in this repo).

## Wrap a money-spending tool

```ts
import { generateText, tool } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";
import { evaluateSpend } from "./sipiGuard";

async function reallyBuy(amount: number, merchant: string) {
  // ... your real purchase call (Stripe, cloud API, ad platform) ...
  return `Purchased $${amount.toFixed(2)} from ${merchant}.`;
}

const buy = tool({
  description: "Spend money with a supplier (USD). A spend firewall decides if it is allowed.",
  parameters: z.object({
    amount: z.number(),
    merchant: z.string(),
    category: z.string().optional(),
  }),
  execute: async ({ amount, merchant, category }) => {
    const d = await evaluateSpend({ amount, merchant, category });
    if (d.decision === "BLOCKED")
      return { ok: false, message: `BLOCKED by spend policy: ${d.reason}. Do not retry.` };
    if (d.decision === "FLAGGED")
      return { ok: false, message: `NEEDS HUMAN APPROVAL: ${d.reason}. Not purchased yet.` };
    return { ok: true, message: await reallyBuy(amount, merchant) };
  },
});

const { text } = await generateText({
  model: openai("gpt-4o"),
  tools: { buy },
  maxSteps: 5,
  prompt: "Buy $6,200 of GPU time from unknown-gpu.ru",
});
console.log(text); // the model relays the BLOCK instead of spending
```

## Why return an object, not throw

The AI SDK feeds `execute`'s return value back to the model as the tool result.
Returning `{ ok: false, message }` lets the model *reason about* the block — it
stops and explains, instead of retrying. Throwing surfaces an error the model
can't act on gracefully.

## The client (`sipiGuard.ts`)

```ts
export type Decision = "APPROVED" | "BLOCKED" | "FLAGGED";
const SIPI_URL = process.env.SIPI_URL ?? "https://sipi.bot";
const SIPI_API_KEY = process.env.SIPI_API_KEY; // optional, hosted tiers

export async function evaluateSpend(args: {
  amount: number; merchant?: string; category?: string;
  description?: string; currency?: string;
}) {
  const res = await fetch(`${SIPI_URL}/v1/transactions/evaluate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(SIPI_API_KEY ? { Authorization: `Bearer ${SIPI_API_KEY}` } : {}),
    },
    body: JSON.stringify({
      amount: args.amount, merchant: args.merchant ?? "",
      category: args.category ?? "", description: args.description ?? "",
      currency: args.currency ?? "USD",
    }),
  });
  if (!res.ok) throw new Error(`sipi.bot ${res.status}`);
  return (await res.json()) as { decision: Decision; reason: string };
}
```

## Set your rules

Defaults: block >$500/tx, >$2,000/day, >10 tx/hour; flag ≥$200. Tune at
https://sipi.bot/dashboard or via `POST /api/rules`. Rule types:
`per_transaction`, `daily_total`, `velocity`, `merchant_block`, `merchant_allow`,
`category_limit`, `time_window`, `approval_threshold`.

- Live + code: https://sipi.bot · eval (53/53): https://sipi.bot/eval
- Source (MIT): https://github.com/kindrat86/sipi-bot · `pip install sipi-bot`
