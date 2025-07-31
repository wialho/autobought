import asyncio
import os
from app.polygon_manager import (
    register_ticker_callback,
    unregister_ticker_callbacks,
    start_websocket
)
from app.polygon_rest import start_rest_polling  # You created this earlier

async def monitor_trading_plan(plan_id, ticker, triggers, length_minutes):
    if os.getenv("POLYGON_API", "REST").upper() == "WEBSOCKET":
        await start_websocket()

        async def on_bar(bar):
            # Trigger logic goes here
            await check_triggers_and_trade(bar, plan_id, triggers)

        register_ticker_callback(ticker, on_bar, plan_id)

        # Sleep for the plan duration
        await asyncio.sleep(length_minutes * 60)
        await unregister_ticker_callbacks(plan_id)

    else:
        await start_rest_polling(ticker, plan_id, triggers, length_minutes)
