#!/bin/bash
# Hermes-cron shim: report new Stripe payments for The HCA Daily.
exec /opt/venv/bin/python3 /data/automation/scripts/stripe_sale_watch.py
