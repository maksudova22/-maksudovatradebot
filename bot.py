print("🔥 НОВИЙ БОТ ЗАПУЩЕНИЙ")

import asyncio
import requests
import pandas as pd
import random

from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

TOKEN = "8593052757:AAGt1P-IZuHz2hxYpfMoxSNZmnfLDDUlux0"
CHANNEL = -1003468351423
MANAGER = "@managfam"

bot = Bot(token=TOKEN)
dp = Dispatcher()

users = set()
wins = 0
losses = 0
user_signals = {}

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Отримати сигнал")],
        [KeyboardButton(text="📈 Статистика")],
        [KeyboardButton(text="💬 Менеджер")]
    ],
    resize_keyboard=True
)

async def check_sub(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "creator", "administrator"]
    except:
        return False

def get_price(symbol):
    if symbol == "FAKE":
        return random.uniform(1, 2)
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    return float(requests.get(url).json()["price"])

def get_candles(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=50"
    data = requests.get(url).json()

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "ct","qv","n","tb","tq","ignore"
    ])

    df["close"] = df["close"].astype(float)
    return df

def calculate_rsi(df, period=14):
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs)).iloc[-1]

def analyze_market():
    pairs = {
        "EUR/USD": "EURUSDT",
        "GBP/USD": "GBPUSDT",
        "AUD/USD": "AUDUSDT",
        "USD/JPY": "JPYUSDT",

        "BTC/USD": "BTCUSDT",
        "ETH/USD": "ETHUSDT",

        "EUR/USD OTC": "FAKE",
        "GBP/USD OTC": "FAKE"
    }

    pair_name, symbol = random.choice(list(pairs.items()))
    direction = random.choice(["ВГОРУ ⬆️", "ВНИЗ ⬇️"])

    return pair_name, symbol, direction

@dp.message(Command("start"))
async def start(message: Message):
    users.add(message.from_user.id)

    if not await check_sub(message.from_user.id):
        await message.answer(f"🔒 Доступ через менеджера:\n{MANAGER}")
        return

    fake_users = random.randint(120, 350)

    await message.answer(f"""
💎 Доступ відкрито
👥 Онлайн: {fake_users}
""", reply_markup=kb)

@dp.message(F.text == "📊 Отримати сигнал")
async def signal(message: Message):
    global wins, losses

    if not await check_sub(message.from_user.id):
        await message.answer(f"🔒 Пиши менеджеру:\n{MANAGER}")
        return

    msg = await message.answer("⏳ Аналізую...")
    await asyncio.sleep(2)

    pair, symbol, direction = analyze_market()

    await message.answer(f"""
🚀 СИГНАЛ

{pair}
{direction}

Вхід через 10 секунд
""")

    await asyncio.sleep(10)

    start_price = get_price(symbol)
    await message.answer("🚀 Вхід")

    await asyncio.sleep(60)
    end_price = get_price(symbol)

    if direction == "ВГОРУ ⬆️":
        result = "ЗАЙШЛО ✅" if end_price > start_price else "НЕ ЗАЙШЛО ❌"
    else:
        result = "ЗАЙШЛО ✅" if end_price < start_price else "НЕ ЗАЙШЛО ❌"

    if result == "ЗАЙШЛО ✅":
        wins += 1
    else:
        losses += 1

    await message.answer(f"📊 {result}")

@dp.message(F.text == "📈 Статистика")
async def stats(message: Message):
    total = wins + losses

    if total == 0:
        await message.answer("Немає даних")
        return

    winrate = round((wins / total) * 100, 1)

    await message.answer(f"""
📊 Статистика
✅ {wins}
❌ {losses}
📈 {winrate}%
""")

@dp.message(F.text == "💬 Менеджер")
async def manager(message: Message):
    await message.answer(MANAGER)

async def main():
    print("🚀 BOT START")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
