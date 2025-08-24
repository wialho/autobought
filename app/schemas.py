from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Annotated, List, Optional
from typing import List, Optional
from pydantic import BaseModel, condecimal
from app.enums import OrderType, VolumeType

class TradeOrderCreate(BaseModel):
    price: Annotated[Decimal, Field(max_digits=10, decimal_places=2)]
    order_type: OrderType
    volume: str  # e.g., number or "all_remaining"
    volume_type: VolumeType
    reasoning: Optional[str] = None

class PlanSequenceCreate(BaseModel):
    repeat: bool = False
    description: Optional[str] = None
    orders: List[TradeOrderCreate]

class TradingPlanCreate(BaseModel):
    ticker: str
    capital: Annotated[Decimal, Field(max_digits=10, decimal_places=2)]
    timeToTrade: str
    description: Optional[str] = None
    tradingPlan: List[PlanSequenceCreate]

