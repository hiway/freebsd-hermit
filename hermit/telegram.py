import os
import logging

from .bot import HermitBot
from .cli import data_dir

from aiogram import Bot, Dispatcher, executor, types

BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
BOT_OWNER = os.environ['TELEGRAM_BOT_OWNER']
BOT_OWNER_ID = int(os.environ['TELEGRAM_BOT_OWNER_ID'])
BOT_NAME = os.environ['TELEGRAM_BOT_NAME']

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
hermit = HermitBot(data_dir, debug=False)


@dp.message_handler(regexp='(^cat[s]?$|puss)')
async def cats(message: types.Message):
    with open('data/cats.jpg', 'rb') as photo:
        await bot.send_photo(message.chat.id, photo, caption='Cats is here 😺',
                             reply_to_message_id=message.message_id)


@dp.message_handler()
async def echo(message: types.Message):
    reply = hermit.reply(message.text)
    await bot.send_message(message.chat.id, reply)


def main():
    executor.start_polling(dp, skip_updates=True)
