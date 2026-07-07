FROM python:3.12-slim

WORKDIR /app

# App code. COPY *.py-style (explicit dir) to avoid the "forgot to add new
# module to COPY" deploy-blocker: we copy the whole package directory.
COPY spendfirewall/ ./spendfirewall/
COPY eval_report.json ./eval_report.json

# Persist SQLite + subscribers on a Fly volume mounted at /data.
ENV SPENDFIREWALL_DB=/data/spendfirewall.db \
    SUBS_FILE=/data/subscribers.txt \
    EVAL_REPORT=/app/eval_report.json \
    PORT=8080

EXPOSE 8080

CMD ["python", "-m", "spendfirewall.api"]
