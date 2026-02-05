#!/usr/bin/env bash
# Start server with 4 workers for concurrency
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 4
