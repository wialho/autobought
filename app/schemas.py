from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum
from typing import List, Optional


class OrderType(str, Enum):
    limit_buy = "limit_buy"
    limit_sell = "limit_sell"
    market_buy = "market_buy"
    market_sell = "market_sell"
    stop_loss = "stop_loss"


class VolumeType(str, Enum):
    greaterthan = "greaterthan"
    lessthan = "lessthan"


class TriggerCreate(BaseModel):
    price: Decimal
    orderType: OrderType
    volume: int
    volumeType: VolumeType


class TradingPlanCreate(BaseModel):
    ticker: str
    triggers: List[TriggerCreate]


class TriggerOut(BaseModel):
    id: int
    price: Decimal
    orderType: OrderType
    volume: int
    volumeType: VolumeType

    class Config:
        orm_mode = True


class TradingPlanOut(BaseModel):
    id: int
    ticker: str
    triggers: List[TriggerOut]

    class Config:
        orm_mode = True


class TradeConfirmationOut(BaseModel):
    id: int
    symbol: str
    quantity: int
    side: str
    timestamp: str

    class Config:
        orm_mode = True
