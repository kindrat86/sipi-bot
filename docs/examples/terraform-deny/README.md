# Minimal fail-closed deny: agent cannot run terraform destroy / apply against prod

This is the 5-line-class rule promised in
[microsoft/autogen#7770](https://github.com/microsoft/autogen/issues/7770).

The agent calls sipi.bot BEFORE executing terraform. Two example decisions:

Allowed (dev workspace):
```json
{
  "merchant": "terraform",
  "description": "terraform plan -workspace=dev",
  "amount": 0,
  "category": "infrastructure"
}
```
Response: `APPROVED`

Denied (prod workspace, destructive):
```json
{
  "merchant": "terraform",
  "description": "terraform apply -auto-approve -workspace=prod",
  "amount": 0,
  "category": "infrastructure"
}
```
Response: `BLOCKED` (pattern rule: `apply|destroy` + `prod` in description)

Fail-closed: when the gate API is unreachable, the wrapper exits non-zero and
terraform never runs. The agent's AWS credentials alone are not sufficient -
the call to the gate is a separate service with its own auth.

Try it live: POST https://sipi.bot/v1/transactions/evaluate ($0.02/call via x402, Base USDC - or free self-hosted, MIT)
