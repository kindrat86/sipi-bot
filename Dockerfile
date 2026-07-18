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

# Persist SQLite + subscribers on a Fly volume mounted at /data.
ENV SPENDFIREWALL_DB=/data/spendfirewall.db \
    SUBS_FILE=/data/subscribers.txt \
    EVAL_REPORT=/app/eval_report.json \
    PUBLIC_DIR=/app/public \
    PORT=8080

EXPOSE 8080

CMD ["python", "-m", "spendfirewall.api"]
