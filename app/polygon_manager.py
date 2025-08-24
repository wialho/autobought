# app/polygon_manager.py

import os
import asyncio
from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage
from collections import defaultdict
from app.discord import send_discord_message

POLYGON_API_TYPE = os.getenv("POLYGON_API", "REST").upper()
POLYGON_WS_URL = os.getenv("POLYGON_WEBSOCKET_BASE_URL")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
AGGREGATES_PER_MINUTE = 'AM'

ticker_callbacks = defaultdict(list)  # { ticker: [(callback_fn, plan_id)] }
active_plan_ids = set()

ws_client: WebSocketClient = None


def register_ticker_callback(ticker: str, callback, plan_id: int):
    ticker_callbacks[ticker.upper()].append((callback, plan_id))
    active_plan_ids.add(plan_id)


async def unregister_ticker_callbacks(plan_id: int):
    global ws_client
    symbols_to_unsubscribe = set()

    for ticker, entries in list(ticker_callbacks.items()):
        new_entries = [(cb, pid) for cb, pid in entries if pid != plan_id]
        if not new_entries:
            symbols_to_unsubscribe.add(ticker)
            del ticker_callbacks[ticker]
        else:
            ticker_callbacks[ticker] = new_entries

    for symbol in symbols_to_unsubscribe:
        await ws_client.unsubscribe(AGGREGATES_PER_MINUTE, symbols=[symbol])
    active_plan_ids.discard(plan_id)


async def start_websocket():
    global ws_client
    if ws_client:
        return  # Already started

    ws_client = WebSocketClient(api_key=POLYGON_API_KEY, url_override=POLYGON_WS_URL)

    @ws_client.on_message()
    async def on_message(msg: WebSocketMessage):
        if msg.channel == AGGREGATES_PER_MINUTE and msg.event_type == "A":
            symbol = msg.symbol.upper()
            for cb, _ in ticker_callbacks.get(symbol, []):
                await cb(msg)

    @ws_client.on_error()
    async def on_error(err):
        plans = ", ".join(str(pid) for pid in active_plan_ids)
        await send_discord_message(f"❌ Polygon WS error (Plans: {plans}): {err}")

    @ws_client.on_close()
    async def on_close():
        plans = ", ".join(str(pid) for pid in active_plan_ids)
        await send_discord_message(f"⚠️ Polygon WS closed (Plans: {plans})")

    await ws_client.connect()
    await ws_client.subscribe(AGGREGATES_PER_MINUTE)
