from sqlalchemy import (
    Column, Integer, String, Numeric, Enum as SqlEnum,
    DateTime, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.enums import OrderType, VolumeType

Base = declarative_base()

class TradingPlan(Base):
    __tablename__ = "trading_plans"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, nullable=False)
    price = Column(Numeric, nullable=False)
    order_type = Column(SqlEnum(OrderType), nullable=False)
    volume = Column(Integer, nullable=False)
    volume_type = Column(SqlEnum(VolumeType), nullable=False)

    # One-to-many relationship
    confirmations = relationship("TradeConfirmation", back_populates="plan", cascade="all, delete-orphan")


class TradeConfirmation(Base):
    __tablename__ = "trade_confirmations"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("trading_plans.id"), nullable=False)
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    side = Column(String, nullable=False)
    alpaca_order_id = Column(String, nullable=False)
    status = Column(String)
    filled_avg_price = Column(Numeric)
    submitted_at = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Many-to-one relationship
    plan = relationship("TradingPlan", back_populates="confirmations")

class Trigger(Base):
    __tablename__ = "triggers"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("trading_plans.id"))
    price = Column(Numeric)
    order_type = Column(SqlEnum(OrderType))
    volume = Column(Integer)
    volume_type = Column(SqlEnum(VolumeType))

    plan = relationship("TradingPlan", back_populates="triggers")


TradingPlan.triggers = relationship("Trigger", back_populates="plan", cascade="all, delete-orphan")
