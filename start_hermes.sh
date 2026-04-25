#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
cd /root/.openclaw/workspace
source .venv/bin/activate
exec python3.11 main.py
