
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.helpers import escape_markdown
from telegram.constants import ParseMode
from datetime import datetime, timezone
import nest_asyncio
import re
nest_asyncio.apply()
from loguru import logger
TOKEN = '7427431349:AAHIC6cgPcK9h4-ysvA-SrKGqZzwROKtF2Y'
CHANNEL_ID = '@newpairsunpump'
GOOD_DEV = '@sunpumpdev'

url_pattern = re.compile(
    r'^(https?:\/\/)?'  # Optional scheme (http or https)
    r'((([\w\d\-_]+\.)+[a-z]{2,})'  # Domain name
    r'|localhost'  # Localhost
    r'|(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))'  # IP address
    r'(:\d+)?'  # Optional port
    r'(\/[\w\d\-._~:\/?#[\]@!$&\'()*+,;=]*)?$'  # Optional path
)

def is_url(string):
    return url_pattern.match(string) is not None

def convert_timestamp_to_human_readable(timestamp):
    readable_date = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    readable_date_str = readable_date.strftime('%Y-%m-%d %H:%M:%S')
    return readable_date_str

async def send_to_telegram(data, channel = 'normal'):
    twitter_ = '✅' if data['twitterUrl'] is not None else '❌'
    telegram_ = '✅' if data['telegramUrl'] is not None else '❌'
    website_ =  '✅' if data['websiteUrl'] is not None else '❌'

    if channel == "dev":
        recent_token = (
            f"`{escape_markdown(data['recentToken'], version=2)}` \| "
            f"\({escape_markdown(data['recentSymbol'], version=2)}\) "
            f"\({escape_markdown('${:,.0f}'.format(data['recentMarketCap']), version=2)}\)"
        )
    else:
        recent_token = "None"

    message = f"""
    
*Mint*: `{escape_markdown(data['contractAddress'], version=2)}`

*Market Cap:* {escape_markdown("${:,.0f}".format(data['marketCap']), version=2)}
*Name*: {escape_markdown(data["name"], version=2)} \({escape_markdown(data['symbol'], version=2)}\)
*Description*: {escape_markdown(data["description"][:500], version=2)}

*Twitter* {escape_markdown(twitter_, version=2)} \| *Telegram* {escape_markdown(telegram_, version=2)} \| *Website* {escape_markdown(website_, version=2)}

*Open time*: {escape_markdown(convert_timestamp_to_human_readable(data['tokenCreatedInstant']), version=2)}

*Recent token: {recent_token}*
"""
    bot_button = [
        InlineKeyboardButton("SunPump BOT", url=f"https://t.me/tron_trading_bot?start=invite_e03746823da74367960aefeb34537ae3"),
        InlineKeyboardButton("MAESTRO BOT", url=f"t.me/maestro?start={data['contractAddress']}-leductam2003"),
        InlineKeyboardButton("SUNDOG BOT", url=f"https://t.me/sundog_trade_bot?start=czxv2rQEcqiI"),
    ]
    bot_button3 = [
        InlineKeyboardButton("Ave.ai", url=f"https://ave.ai/token/{data['contractAddress']}-tron?from=Default"),
        InlineKeyboardButton("Sunpump.meme", url='https://sunpump.meme/token/' + data['contractAddress']),
    ]
    keyboard = []
    if data.get('twitterUrl') and is_url(data.get('twitterUrl')):
        keyboard.append(InlineKeyboardButton("Twitter", url=data['twitterUrl']))

    if data.get('telegramUrl') and is_url(data.get('telegramUrl')):
        keyboard.append(InlineKeyboardButton("Telegram", url=data['telegramUrl']))

    if data.get('websiteUrl') and (is_url(data.get('websiteUrl'))):
        keyboard.append(InlineKeyboardButton("Website", url=data['websiteUrl']))

    reply_markup = InlineKeyboardMarkup([keyboard, bot_button3, bot_button])
    bot = Bot(token=TOKEN)
    logger.info(f"{data['name']} - {data['contractAddress']}")
    chat_id = CHANNEL_ID if channel == 'normal' else GOOD_DEV
    return await bot.send_photo(chat_id=chat_id, photo=data['logoUrl'], caption=message, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=reply_markup)