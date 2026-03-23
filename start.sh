#!/bin/bash

if [ "$SERVICE_TYPE" = "worker" ]; then
    echo "Starting worker..."
    exec python -m whatsapp_langchain.worker.main
else
    echo "Starting web server..."
    exec uvicorn whatsapp_langchain.server.main:app --host 0.0.0.0 --port ${PORT:-8000}
fi
