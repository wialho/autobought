import asyncio
import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from app.db import SessionLocal
from app.discord import send_discord_message
from app.models import TradeConfirmation

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_PAPER = "paper" in os.getenv("ALPACA_BASE_URL", "")

trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=ALPACA_PAPER)

def place_order(symbol: str, qty: int, side: str, plan_id: int):
    order_request = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
        time_in_force=TimeInForce.GTC
    )
    order = trading_client.submit_order(order_request)

    session = SessionLocal()
    try:
        confirmation = TradeConfirmation(
            plan_id=plan_id,
            symbol=symbol,
            quantity=qty,
            side=side
        )
        session.add(confirmation)
        session.commit()

        # Notify Discord (run outside of event loop context)
        asyncio.create_task(send_discord_message(
            f"✅ Trade executed for Plan `{plan_id}`: `{side.upper()}` {qty} shares of `{symbol}`"
        ))

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

    return order.dict()