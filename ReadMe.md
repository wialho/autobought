### AutoBought

This is a automated trading program that uses a trading plan to execute

## Getting Started

1. clone this repo
2. install docker desktop https://docs.docker.com/get-started/get-docker/
3. rename `.env.example` to `.env`
4. replace the values in the env with your api key values (alpaca and polygon)
   - to sign up for alpaca go here https://alpaca.markets/
     - after signup, get your key and secret from your profile
   - to sign up for polygon go here https://polygon.io/
     - your key should be on the dashboard
     - websockets use a paid plan and the rest api uses the free plan, to toggle between change `POLYGON_API` to `WEBSOCKET` instead of `REST`
5. go to your personal discord server and hit the settings button, select integrations, then webhook, then add a webhook. Copy that webhook url and update the env with that value
6. in the commandline at the top level of the folder (where the dockerfile is) run the command ` Docker compose up --build`
7. go to http://localhost:8000/docs#/ in a browser and use the api to enter trading plans

## Trading Plan

Currently Autobought has one endpoint which accepts a json object (see example below)

`ticker: string - ticker you want to trade`
`capital: int - dollar amount you want to trade`
`timeToTrade: string - this is an integer with an enum (month/day/hour)`
`tradingPlan: TradingPlan[] - this is a list of trades to execute`

Trading Plan Object
`repeat: boolean - should trade repeat if conditions are met`
`orders: Order[] - a list of orders to place`

Order Object
`price: double - price to buy or sell`
`orderType: enum - type of buy or sell (limit_buy/limit_sell/market_buy/market_sell/stop_loss)`
`volume: int - volume to trade on in millions`
`volumeType: enum - type of volume trade (ignore/greater_than/less_than)`

# Example (This example is a merger arbitrage)

```
 {
  "ticker": "STAA",
  "capital": 10000,
  "timeToTrade": "3 month",
  "tradingPlan": [
    {
      "repeat": false,
      "orders": [
        {
          "price": 26.70,
          "orderType": "limit_buy",
          "volume": 374,
          "volumeType": "ignore",
        },
        {
          "price": 27.95,
          "orderType": "limit_sell",
          "volume": 374,
          "volumeType": "ignore",
        },
        {
          "price": 25.50,
          "orderType": "stop_loss",
          "volume": 374,
          "volumeType": "ignore",
        }
      ]
    },
    {
      "repeat": false,
      "orders": [
        {
          "price": 26.30,
          "orderType": "limit_buy",
          "volume": 190,
          "volumeType": "ignore",
        },
        {
          "price": 27.90,
          "orderType": "limit_sell",
          "volume": 190,
          "volumeType": "ignore",
        },
        {
          "price": 24.00,
          "orderType": "stop_loss",
          "volume": 190,
          "volumeType": "ignore",
        }
      ]
    },
  ],
}
```
