# Intentguard
Everything becomes “validated intent + normalized data” inside
# INTENTGUARD – V1

A prevention-first data execution engine.

## Core Idea
User defines intent.
System enforces it safely.

## Features
- Intent-driven validation
- Data cleaning
- Safe output routing
- Execution memory (audit)

## Run locally
pip install -r requirements.txt
streamlit run ui/streamlit_app.py

## Render Start Command
streamlit run ui/streamlit_app.py --server.port $PORT --server.address 0.0.0.0
