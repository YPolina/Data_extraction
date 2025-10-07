#!/bin/bash

set -e
# Step 1: Run data collection + processing

if [ "$DATA_COLLECTION" = "True" ]; then
    python src/main.py --query "$QUERY" --retmax "$RETMAX" --data_collection
else
    python src/main.py --query "$QUERY" --retmax "$RETMAX"
fi

# Step 2: Launch Streamlit interface
streamlit run src/api/app.py --server.port ${STREAMLIT_PORT:-8501} --server.address 0.0.0.0