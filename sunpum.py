from loguru import logger
import requests
import telegram_helper
import asyncio
from datetime import datetime, timedelta
import json
import time
import aiohttp
import asyncio

class SUNPUMP:
    def __init__(self) -> None:
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }
        self.processed_mints = set()
        self.validated_websites = {}

    def is_recent(self, timestamp):
        current_time = datetime.now()
        five_minutes_ago = current_time - timedelta(minutes=3)
        return datetime.fromtimestamp(timestamp) > five_minutes_ago

    async def fetch_good_dev(self):
        got_response = False
        page = 1
        all_tokens = []
        async with aiohttp.ClientSession(headers=self.headers) as session:
            while not got_response:
                try:
                    async with session.get(f'https://api.sunpump.meme/pump-api/token/search?onSunSwap=true&page={page}&size=24&sort=tokenCreatedInstant:DESC',timeout=10) as response:
                        if response.status == 500:
                            logger.warning(f"Server error (500) at page {page}. Skipping this page and continuing.")
                            page += 1
                            continue
                        if response.status == 200:
                            tokens = await response.json()
                            tokens = tokens.get('data', {}).get('tokens', [])
                            if len(tokens) == 0:
                                got_response = True
                            else:
                                logger.info(len(tokens))
                                all_tokens.extend(tokens)
                                page += 1
                        else:
                            logger.error(f"Error: {response.status} - {response.reason}")
                except Exception as err:
                    logger.error(f"Exception occurred: {err}")
            
        good = []
        for token in all_tokens:
            if token['marketCap'] > 200000:
                good.append({
                    "owner": token['ownerAddress'], 
                    "recentToken": token["contractAddress"], 
                    "symbol": token["symbol"], 
                    "marketCap": token["marketCap"]
                })
        
        good.append({
            "owner" : "TF625zF8kUZjyz244ZKqrzX3YGip5f9NKZ",
            "recentToken" : "黑客",
            "symbol" : "黑客",
            "marketCap" : "黑客"
        })
        with open('dev.json', 'w') as f:
            json.dump(good, f, indent=4)

    async def fetch_data(self):
        got_response = False
        async with aiohttp.ClientSession(headers=self.headers) as session:
            while not got_response:
                try:
                    async with session.get('https://api.sunpump.meme/pump-api/token/search?page=1&size=24&sort=tokenCreatedInstant:DESC',timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data['data']['tokens']
                        else:
                            logger.error(response.reason)
                except Exception as err:
                    logger.error(err)

    async def new_launch(self):
        try:
            logger.debug("Fetching data...")
            data = await self.fetch_data()

            if data is None:
                logger.error("Fetched data is None")
                return

            if not isinstance(data, list):
                logger.error("Fetched data is not a list")
                return

            new_tokens = sorted(
                [item for item in data if item['contractAddress'] not in self.processed_mints and self.is_recent(item['tokenCreatedInstant'])],
                key=lambda x: x['tokenCreatedInstant'],
                reverse=True
            )

            with open('dev.json', 'r') as f:
                dev = json.loads(f.read())

            if not isinstance(dev, list):
                logger.error("Dev data is not a list")
                return

            for token in new_tokens:
                logger.debug(f"Processing token: {token['contractAddress']}")
                self.processed_mints.add(token['contractAddress'])
                sent_to_dev = False
                for item in dev:
                    if 'owner' in item and item['owner'] == token.get('ownerAddress'):
                        token['recentToken'] = item.get('recentToken', 'N/A')
                        token['recentSymbol'] = item.get('symbol', 'N/A')
                        token['recentMarketCap'] = item.get('marketCap', 'N/A')
                        await telegram_helper.send_to_telegram(token, 'normal')
                        await telegram_helper.send_to_telegram(token, 'dev')
                        sent_to_dev = True
                        break
                
                if not sent_to_dev:
                    await telegram_helper.send_to_telegram(token, 'normal')

        except Exception as err:
            logger.error(f"An error occurred: {err}")

    async def run_fetch_good_dev(self):
        while True:
            await self.fetch_good_dev()
            await asyncio.sleep(500)

    async def new_launch_loop(self):
        while True:
            await self.new_launch()    

async def main():
    pumpfun = SUNPUMP()
    fetch_good_dev_task = asyncio.create_task(pumpfun.run_fetch_good_dev())
    new_launch_task = asyncio.create_task(pumpfun.new_launch_loop())
    await asyncio.gather(fetch_good_dev_task, new_launch_task)

if __name__ == "__main__":
    asyncio.run(main())
