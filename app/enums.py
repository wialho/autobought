from enum import Enum

class OrderType(str, Enum):
    MARKET_BUY = "market_buy"
    MARKET_SELL = "market_sell"
    LIMIT_BUY = "limit_buy"
    LIMIT_SELL = "limit_sell"
    STOP_LOSS = "stop_loss"

class VolumeType(str, Enum):
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IGNORE = 'ignore'

class TradeTime(str, Enum):
    MONTH = 'month',
    DAY = 'day',
    HOUR = 'hour'