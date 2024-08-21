from loguru import logger
import requests
from datetime import datetime, timedelta
import json

class SUNPUMP:
    def __init__(self) -> None:
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }
        self.processed_mints = set()
        self.validated_websites = {}

    def fetch_data(self):
        got_response = False
        page = 1
        all_tokens = []
        while not got_response:
            try:
                response = requests.get(f'https://api.sunpump.meme/pump-api/token/search?onSunSwap=true&page={page}&size=24&sort=tokenCreatedInstant:DESC', headers=self.headers)
                if response.status_code == 500:
                    logger.warning(f"Server error (500) at page {page}. Skipping this page and continuing.")
                    page += 1
                    continue
                if response.status_code == 200:
                    tokens = response.json().get('data', {}).get('tokens', [])
                    if len(tokens) == 0:
                        got_response = True
                    else:
                        logger.info(len(tokens))
                        all_tokens.extend(tokens)
                        page += 1
                else:
                    logger.error(f"Error: {response.status_code} - {response.reason}")
            except Exception as err:
                logger.error(f"Exception occurred: {err}")

        good = []
        for token in all_tokens:
            if token['marketCap'] > 100000:
                good.append({"owner" : token['ownerAddress'], "recentToken" : token["contractAddress"]})
        with open('dev.json', 'w') as f:
            json.dump(good, f, indent=4)


def main():
    pumpfun = SUNPUMP()
    pumpfun.fetch_data()

if __name__ == "__main__":
    main()
