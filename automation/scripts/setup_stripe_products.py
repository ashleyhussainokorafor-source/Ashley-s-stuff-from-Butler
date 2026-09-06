#!/usr/bin/env python3
"""
Autonomous Stripe Product & Payment Link Generator for The HCA Daily
"""

import urllib.request
import urllib.parse
import json
import base64
import os
import sys

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")

def stripe_request(endpoint, data=None, method="POST"):
    url = f"https://api.stripe.com/v1/{endpoint}"
    encoded_data = urllib.parse.urlencode(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=encoded_data, method=method)
    auth_header = "Basic " + base64.b64encode(f"{STRIPE_SECRET_KEY}:".encode("utf-8")).decode("utf-8")
    req.add_header("Authorization", auth_header)
    if data:
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def create_product(name, description):
    data = {
        "name": name,
        "description": description
    }
    prod = stripe_request("products", data)
    return prod["id"]

def create_price(product_id, unit_amount, currency="usd", recurring_interval=None):
    data = {
        "product": product_id,
        "unit_amount": unit_amount,
        "currency": currency
    }
    if recurring_interval:
        data["recurring[interval]"] = recurring_interval
    price = stripe_request("prices", data)
    return price["id"]

def create_payment_link(price_id):
    data = {
        "line_items[0][price]": price_id,
        "line_items[0][quantity]": 1
    }
    plink = stripe_request("payment_links", data)
    return plink["url"]

def build_all():
    catalog = [
        {
            "name": "HCA Career Navigator (Monthly)",
            "description": "Unlimited 24/7 AI career advisor, line-by-line resume reviews, and salary negotiation playbooks.",
            "amount": 2900, # $29.00
            "interval": "month"
        },
        {
            "name": "HCA Career Navigator (Annual)",
            "description": "Full year of unlimited AI career advisory + 1 free mock interview session every month (Save over 40%).",
            "amount": 19900, # $199.00
            "interval": "year"
        },
        {
            "name": "HCA Interview Coach (Single Session)",
            "description": "1 complete role-tailored mock interview simulation with real-time STAR feedback & Executive Scorecard.",
            "amount": 1900, # $19.00
            "interval": None
        },
        {
            "name": "HCA Interview Coach (3-Session Prep Pack)",
            "description": "3 full interview simulations + follow-up drilling & candidate readiness score.",
            "amount": 4900, # $49.00
            "interval": None
        }
    ]

    results = {}
    for item in catalog:
        print(f"Creating Product: {item['name']}...")
        prod_id = create_product(item["name"], item["description"])
        print(f"  -> Product ID: {prod_id}")
        
        price_id = create_price(prod_id, item["amount"], recurring_interval=item["interval"])
        print(f"  -> Price ID: {price_id}")
        
        plink_url = create_payment_link(price_id)
        print(f"  -> Live Payment Link: {plink_url}\n")
        
        results[item["name"]] = {
            "product_id": prod_id,
            "price_id": price_id,
            "payment_link": plink_url
        }
        
    out_file = "/data/business/hca-daily/live_payment_links.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Catalog complete! Stored in {out_file}")
    return results

if __name__ == "__main__":
    build_all()
