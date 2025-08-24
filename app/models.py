from enum import Enum
from sqlalchemy import (
    Boolean, Column, Integer, String, Numeric, Enum as SqlEnum,
    DateTime, ForeignKey, Text
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
    capital = Column(Numeric, nullable=False)
    time_to_trade = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    sequences = relationship("PlanSequence", back_populates="plan", cascade="all, delete-orphan")
    confirmations = relationship("TradeConfirmation", back_populates="plan")

class PlanSequence(Base):
    __tablename__ = "plan_sequences"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("trading_plans.id"), nullable=False)
    repeat = Column(Boolean, default=False)
    description = Column(Text, nullable=True)

    plan = relationship("TradingPlan", back_populates="sequences")
    orders = relationship("TradeOrder", back_populates="sequence", cascade="all, delete-orphan")

class TradeOrder(Base):
    __tablename__ = "trade_orders"

    id = Column(Integer, primary_key=True, index=True)
    sequence_id = Column(Integer, ForeignKey("plan_sequences.id"), nullable=False)
    price = Column(Numeric, nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    volume = Column(String, nullable=False)  # supports integers or "all_remaining"
    volume_type = Column(Enum(VolumeType), nullable=False)
    reasoning = Column(Text, nullable=True)

    sequence = relationship("PlanSequence", back_populates="orders")

class TradeConfirmation(Base):
    __tablename__ = "trade_confirmations"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("trading_plans.id"), nullable=False)
    symbol = Column(String, nullable=False)
    quantity = Column(String, nullable=False)
    side = Column(String, nullable=False)

    plan = relationship("TradingPlan", back_populates="confirmations")
