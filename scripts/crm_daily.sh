#!/bin/bash
# Personal CRM daily nudge (quiet when nothing due). Runs the CRM agent.
cd /data/personal/relationships
exec python3 crm_nudge.py