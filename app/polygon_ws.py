import os
import asyncio
from polygon.websocket.models import WebSocketMessage
from polygon.websocket.client import WebSocketClient
from polygon.websocket.enums import WebSocketChannel
from collections import defaultdict

from app.discord import send_discord_message

POLYGON_WS_URL = os.getenv("POLYGON_WEBSOCKET_BASE_URL")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

# Keeps active callbacks for ticker listeners
ticker_callbacks = defaultdict(list)


active_plan_ids = set()

def register_ticker_callback(ticker: str, callback, plan_id: int):
    ticker_callbacks[ticker.upper()].append((callback, plan_id))
    active_plan_ids.add(plan_id)


async def handle_aggregate_bar(msg: WebSocketMessage):
    """
    Handles the received 5-minute aggregate bar update
    """
    if msg.symbol in ticker_callbacks:
        for callback in ticker_callbacks[msg.symbol]:
            await callback(msg)


async def connect_polygon_ws():
    client = WebSocketClient(api_key=POLYGON_API_KEY, url_override=POLYGON_WS_URL)

    @client.on_message()
    async def on_message(msg: WebSocketMessage):
        if msg.channel == WebSocketChannel.AGGREGATES_PER_MINUTE and msg.event_type == "A":
            await handle_aggregate_bar(msg)

    @client.on_error()
    async def on_error(err):
        plan_list = ", ".join(str(pid) for pid in active_plan_ids)
        await send_discord_message(f"❌ Polygon WebSocket error (Plans: {plan_list}): {err}")

    @client.on_close()
    async def on_close():
        plan_list = ", ".join(str(pid) for pid in active_plan_ids)
        await send_discord_message(f"⚠️ Polygon WebSocket closed (Plans: {plan_list})")


    await client.connect()
    await client.subscribe(WebSocketChannel.AGGREGATES_PER_MINUTE)

    # Re-subscribe to all tickers previously registered
    for symbol in ticker_callbacks:
        await client.subscribe(WebSocketChannel.AGGREGATES_PER_MINUTE, symbols=[symbol])

async def unregister_ticker_callbacks(client: WebSocketClient, plan_id: int):
    symbols_to_unsubscribe = set()

    for ticker, entries in list(ticker_callbacks.items()):
        new_entries = [(cb, pid) for cb, pid in entries if pid != plan_id]
        if not new_entries:
            symbols_to_unsubscribe.add(ticker)
            del ticker_callbacks[ticker]
        else:
            ticker_callbacks[ticker] = new_entries

    for symbol in symbols_to_unsubscribe:
        await client.unsubscribe(WebSocketChannel.AGGREGATES_PER_MINUTE, symbols=[symbol])
