# main.py

import asyncio
from contextlib import asynccontextmanager
import os
import uvicorn
from fastapi import Depends, FastAPI, BackgroundTasks
from app import schemas
from app import models
from app.alembic_runner import run_migrations
from app.db import engine, get_db
from app.models import Base
from app.schemas import TradingPlanCreate
from app.models import TradingPlan
from app.polygon_rest import start_rest_polling
from app.polygon_manager import start_websocket, register_ticker_callback, unregister_ticker_callbacks
from app.discord import send_discord_message
from sqlalchemy.orm import Session

from app.trading_logic import start_trading_for_plan

@asynccontextmanager
async def lifespan(app: FastAPI):
        run_migrations()
        # Base.metadata.create_all(bind=engine)
        
        yield

app = FastAPI(lifespan=lifespan)

@app.post("/trading-plan")
async def create_trading_plan(
    plan_data: schemas.TradingPlanCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    plan = models.TradingPlan(
        ticker=plan_data.ticker,
        capital=plan_data.capital,
        time_to_trade=plan_data.timeToTrade,
        description=plan_data.description,
    )
    db.add(plan)
    db.flush()  # Get plan.id

    for seq in plan_data.tradingPlan:
        sequence = models.PlanSequence(
            plan_id=plan.id,
            repeat=seq.repeat,
            description=seq.description,
        )
        db.add(sequence)
        db.flush()

        for order in seq.orders:
            trade_order = models.TradeOrder(
                sequence_id=sequence.id,
                price=order.price,
                order_type=order.order_type,
                volume=order.volume,
                volume_type=order.volume_type,
                reasoning=order.reasoning,
            )
            db.add(trade_order)

    db.commit()

    
    await send_discord_message(f"🟢 Trading plan {plan.id} started for {plan.ticker}")

    background_tasks.add_task(start_trading_for_plan, plan.id)

    return {"status": "started", "plan_id": plan.id}
    
