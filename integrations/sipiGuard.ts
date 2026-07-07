/**
 * sipiGuard.ts — zero-dependency client for the sipi.bot spend firewall.
 * Works in Node 18+ (global fetch) and edge runtimes.
 */
export type Decision = "APPROVED" | "BLOCKED" | "FLAGGED";
export interface EvalResult {
  decision: Decision;
  reason: string;
  amount: number;
  merchant: string;
  category: string;
}

const SIPI_URL = process.env.SIPI_URL ?? "https://sipi.bot";
const SIPI_API_KEY = process.env.SIPI_API_KEY; // optional, for hosted tiers

export async function evaluateSpend(args: {
  amount: number;
  merchant?: string;
  category?: string;
  description?: string;
  currency?: string;
}): Promise<EvalResult> {
  const res = await fetch(`${SIPI_URL}/v1/transactions/evaluate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(SIPI_API_KEY ? { Authorization: `Bearer ${SIPI_API_KEY}` } : {}),
    },
    body: JSON.stringify({
      amount: args.amount,
      merchant: args.merchant ?? "",
      category: args.category ?? "",
      description: args.description ?? "",
      currency: args.currency ?? "USD",
    }),
  });
  if (!res.ok) throw new Error(`sipi.bot ${res.status}`);
  return (await res.json()) as EvalResult;
}
