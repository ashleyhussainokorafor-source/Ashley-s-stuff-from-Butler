#!/bin/bash
# Thin shim so the Hermes cron scheduler (which requires scripts inside the
# profile's scripts dir) can run the HCA Daily lead drip engine.
exec bash /data/business/hca-daily/email/drip_wrapper.sh