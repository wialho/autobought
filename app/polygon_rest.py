# app/polygon_rest.py

import os
import time
import asyncio
import httpx
from app.alpaca import place_order
from app.discord import send_discord_message
from app.enums import VolumeType
from decimal import Decimal

POLYGON_REST_BASE_URL = os.getenv("POLYGON_REST_BASE_URL")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")


async def start_rest_polling(ticker: str, plan_id: int, triggers: list[dict], duration_minutes: int):
    end_time = time.time() + (duration_minutes * 60)

    while time.time() < end_time:
        try:
            bar = await get_latest_5min_bar(ticker)
            if bar:
                await process_triggers(plan_id, ticker, bar, triggers)
        except Exception as e:
            await send_discord_message(f"❗ REST polling error for plan {plan_id}: {str(e)}")
        await asyncio.sleep(300)  # Wait 5 minutes


async def get_latest_5min_bar(ticker: str):
    url = f"{POLYGON_REST_BASE_URL}/v2/aggs/ticker/{ticker}/range/5/minute/1?apiKey={POLYGON_API_KEY}&limit=1&sort=desc"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()

        if "results" in data and data["results"]:
            bar = data["results"][0]
            return {
                "symbol": ticker,
                "price": Decimal(str(bar["c"])),  # close price
                "volume": bar["v"]
            }
    return None


async def process_triggers(plan_id: int, symbol: str, bar_data: dict, triggers: list[dict]):
    for trigger in triggers:
        price = Decimal(str(trigger["price"]))
        volume = int(trigger["volume"])
        volume_type = trigger["volumeType"]
        order_type = trigger["orderType"].lower()
        side = "buy" if "buy" in order_type else "sell"
        should_execute = False

        # Price logic (can be expanded with more rules)
        if side == "buy" and bar_data["price"] <= price:
            should_execute = True
        elif side == "sell" and bar_data["price"] >= price:
            should_execute = True

        # Volume condition
        if volume_type == VolumeType.LESSTHAN and bar_data["volume"] >= volume:
            should_execute = False
        elif volume_type == VolumeType.GREATERTHAN and bar_data["volume"] <= volume:
            should_execute = False

        if should_execute:
            result = place_order(symbol=symbol, qty=1, side=side, plan_id=plan_id)
            await send_discord_message(f"📈 {side.upper()} order placed via REST for plan {plan_id}: {result}")
