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
