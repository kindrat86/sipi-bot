FROM python:3.12-slim

WORKDIR /app

# App code. COPY *.py-style (explicit dir) to avoid the "forgot to add new
# module to COPY" deploy-blocker: we copy the whole package directory.
COPY spendfirewall/ ./spendfirewall/
COPY eval_report.json ./eval_report.json
COPY public/ ./public/

# pSEO static pages
COPY vs/ ./vs/
COPY for/ ./for/
COPY learn/ ./learn/
COPY integrations/ ./integrations/
COPY faq/ ./faq/
COPY use-cases/ ./use-cases/
COPY glossary/ ./glossary/
COPY alternatives-to/ ./alternatives-to/
COPY benchmarks/ ./benchmarks/
# Round 16 new page types
COPY tutorials/ ./tutorials/
COPY policies/ ./policies/
COPY limits/ ./limits/
# Round 15 Isenberg pSEO
COPY best/ ./best/
COPY how-to/ ./how-to/
# Round 19 Isenberg pSEO (templates, cost-of)
COPY templates/ ./templates/
COPY cost-of/ ./cost-of/

# 2026-07-18 pSEO expansion
COPY scenarios/ ./scenarios/
COPY redflags/ ./redflags/
COPY calculators/ ./calculators/
COPY guides/ ./guides/

# 2026-07-27 traffic program — open incident database + freshness surfaces.
# Generators live in lib/ (shared chrome) and write these section dirs at repo
# root; api.py:_serve_pseo() serves them. public/data/ holds the CC BY 4.0
# dataset endpoints (json/csv/jsonl/jsonld) referenced by llms.txt.
COPY incidents/ ./incidents/
COPY blog/ ./blog/
COPY tools/ ./tools/
COPY changelog/ ./changelog/
COPY status/ ./status/
COPY sectors/ ./sectors/
COPY errors/ ./errors/
COPY pricing-questions/ ./pricing-questions/
COPY public/data/ ./public/data/
# Verify the new content landed — fails the build with a clear error if COPY
# silently produced nothing (e.g. Depot context exclusion or dir mismatch).
RUN test -f ./incidents/index.html || (echo "ERROR: incidents/index.html missing after COPY" && exit 1)
RUN test -f ./blog/index.html    || (echo "ERROR: blog/index.html missing after COPY" && exit 1)
RUN test -f ./changelog/index.html || (echo "ERROR: changelog/index.html missing after COPY" && exit 1)
RUN test -f ./status/index.html  || (echo "ERROR: status/index.html missing after COPY" && exit 1)
RUN test -f ./tools/index.html   || (echo "ERROR: tools/index.html missing after COPY" && exit 1)

# --- structured-data gate (~/.growth-engine/GUARDRAILS.md rule 3) ---
# Fails the image build — and so `flyctl deploy` — if any copied page carries
# unparsable JSON-LD. This runs after every COPY above so it sees exactly the
# page set the container will serve, which a lint on the checkout cannot
# guarantee. The gate is what was missing when "Unparsable structured data —
# Parsing error: Missing ',' or '}'" reached Search Console on voicelogpro.com.
# Python, not the portfolio's Node gate, deliberately: this is a python:slim
# image and validate_jsonld.py is stdlib-only, so gating costs no new
# dependency and no Node install. scripts/verify-jsonld.mjs runs in CI instead,
# where Node is free, for the extra corruption-signature checks.
COPY scripts/validate_jsonld.py /tmp/validate_jsonld.py
RUN python3 /tmp/validate_jsonld.py . && rm /tmp/validate_jsonld.py

# Persist SQLite + subscribers on a Fly volume mounted at /data.
ENV SPENDFIREWALL_DB=/data/spendfirewall.db \
    SUBS_FILE=/data/subscribers.txt \
    EVAL_REPORT=/app/eval_report.json \
    PUBLIC_DIR=/app/public \
    PORT=8080

EXPOSE 8080

CMD ["python", "-m", "spendfirewall.api"]
