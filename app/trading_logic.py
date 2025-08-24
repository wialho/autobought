from app.models import TradingPlan, TradeOrder, PlanSequence
from app.alpaca import place_order
from app.polygon_ws import PolygonWebSocketClient
from app.polygon_rest import get_latest_price
from app.db import SessionLocal
from app.enums import OrderType, VolumeType
import os
import time
import logging

logger = logging.getLogger(__name__)

POLYGON_API_TYPE = os.getenv("POLYGON_API", "WEBSOCKET").upper()

def start_trading_for_plan(plan_id: int):
    db = SessionLocal()
    try:
        plan = db.query(TradingPlan).filter(TradingPlan.id == plan_id).first()
        if not plan:
            logger.error(f"Plan ID {plan_id} not found.")
            return

        logger.info(f"Starting trading for plan ID {plan_id} using {POLYGON_API_TYPE} API")

        if POLYGON_API_TYPE == "WEBSOCKET":
            ws_client = PolygonWebSocketClient()
            ws_client.subscribe(plan.ticker)
        else:
            ws_client = None  # not needed for REST

        for sequence in plan.sequences:
            executed_orders = set()
            while True:
                # Get market data
                if POLYGON_API_TYPE == "WEBSOCKET":
                    data = ws_client.get_latest_price(plan.ticker)
                else:
                    data = get_latest_price(plan.ticker)

                if not data:
                    logger.warning(f"No market data available for {plan.ticker}")
                    time.sleep(300)
                    continue

                current_price = data.get("price")

                for order in sequence.orders:
                    if order.id in executed_orders:
                        continue

                    match = False

                    if order.volume_type == VolumeType.IGNORE:
                        match = True
                    elif order.volume_type == VolumeType.GREATERTHAN:
                        match = data.get("volume", 0) > order.volume
                    elif order.volume_type == VolumeType.LESSTHAN:
                        match = data.get("volume", 0) < order.volume

                    if match:
                        should_execute = False
                        if order.order_type in [OrderType.LIMITBUY, OrderType.STOPLOSS]:
                            should_execute = current_price <= float(order.price)
                        elif order.order_type in [OrderType.LIMITSELL, OrderType.MARKETSELL]:
                            should_execute = current_price >= float(order.price)

                        if should_execute:
                            qty = (
                                int(plan.capital // float(order.price))
                                if order.volume == "all_remaining"
                                else int(order.volume)
                            )
                            place_order(
                                plan.ticker,
                                qty,
                                order.order_type.name.replace("limit", "").replace("market", "").replace("stop", ""),
                                plan_id,
                            )
                            executed_orders.add(order.id)
                            logger.info(f"Executed order {order.id} for plan {plan_id}")

                if not sequence.repeat:
                    break
                time.sleep(300)  # Check again in 5 minutes

        if POLYGON_API_TYPE == "WEBSOCKET" and ws_client:
            ws_client.unsubscribe(plan.ticker)
            ws_client.close()

        logger.info(f"Finished executing trading plan ID {plan_id}")
    except Exception as e:
        logger.error(f"Error in trading plan {plan_id}: {e}")
    finally:
        db.close()
