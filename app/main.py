# main.py

import asyncio
import os
import uvicorn
from fastapi import FastAPI, BackgroundTasks
from app.alembic_runner import run_migrations
from app.db import Base, engine
from app.schemas import TradingPlanCreate
from app.models import TradingPlan
from app.polygon_rest import start_rest_polling
from app.polygon_manager import start_websocket, register_ticker_callback, unregister_ticker_callbacks
from app.discord import send_discord_message
from sqlalchemy.orm import Session

app = FastAPI()

@app.on_event("startup")
async def startup():
    run_migrations()
    Base.metadata.create_all(bind=engine)


@app.post("/trading-plan")
async def create_trading_plan(plan: TradingPlanCreate, background_tasks: BackgroundTasks):
    db = Session(bind=engine)
    db_plan = TradingPlan(
        ticker=plan.ticker,
        triggers=plan.triggers,
        length_minutes=plan.length_minutes
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)

    await send_discord_message(f"🟢 Trading plan {db_plan.id} started for {db_plan.ticker}")

    # Conditionally run background task
    if os.getenv("POLYGON_API", "REST").upper() == "WEBSOCKET":
        async def on_bar(bar):
            # Do your trigger logic here
            ...

        await start_websocket()
        register_ticker_callback(plan.ticker, on_bar, db_plan.id)
        background_tasks.add_task(asyncio.sleep, plan.length_minutes * 60)
        background_tasks.add_task(unregister_ticker_callbacks, db_plan.id)
    else:
        background_tasks.add_task(
            start_rest_polling,
            plan.ticker,
            db_plan.id,
            plan.triggers,
            plan.length_minutes
        )

    return {"status": "started", "plan_id": db_plan.id}
