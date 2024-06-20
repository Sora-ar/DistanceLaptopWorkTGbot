from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv
import os
import subprocess
import logging
import asyncio
from work_db import add_site, get_last_sites

load_dotenv()

TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
MAC_ADDRESS = os.getenv('MAC_ADDRESS')

bot = Bot(token=TELEGRAM_API_TOKEN, proxy='http://proxy.server:3128')
dp = Dispatcher()


async def wake_on_lan(mac_address):
    try:
        subprocess.call(['wakeonlan', mac_address])
    except Exception as e:
        logging.error(f"Error: {e}")


# /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    try:
        start_message = (
            "Привет! Я бот для управления вашим ноутбуком.\n"
            "Вот список доступных команд:\n"
            "   /help - Показать перечень доступных команд\n"
        )
        await message.answer(start_message)
    except Exception as e:
        logging.error(f"Error: {e}")


# /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    try:
        help_message = (
            "Перечень доступных команд:\n"
            "   /start - Показать приветственное сообщение\n"
            "   /help - Показать перечень доступных команд\n"
            "   /shutdown - Выключить ноутбук\n"
            "   /wake - Включить ноутбук\n"
            "   /open_app <название_приложения> - Открыть указанное приложение\n"
            "   /open_site <url> - Открыть сайт и запомнить его\n"
        )
        await message.answer(help_message)
    except Exception as e:
        logging.error(f"Error: {e}")


# /shutdown
@dp.message(Command("shutdown"))
async def cmd_shutdown(message: Message):
    try:
        os.system('shutdown /s /t 0 /f')
        await message.answer("Ноутбук выключается...")
    except Exception as e:
        logging.error(f"Error: {e}")


# /wake
@dp.message(Command("wake"))
async def cmd_wake(message: Message):
    try:
        await wake_on_lan(MAC_ADDRESS)
        await message.answer("Отправляю сигнал Wake-on-LAN...")
    except Exception as e:
        logging.error(f"Error: {e}")


def find_executable(app_name):
    system_paths = [
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        "C:\\Users\\Admin\\AppData\\Local",
        "C:\\Users\\Admin\\AppData\\Roaming",
        "C:\\Windows\\System32",
    ]
    app_name = app_name.lower()

    for path in system_paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.lower() == f"{app_name}.exe":
                    return os.path.join(root, file)
    return None


# /open_app
@dp.message(Command("open_app"))
async def cmd_open_app(message: Message):
    try:
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            app_name = args[1]
            app_path = find_executable(app_name)
            if app_path:
                subprocess.Popen(app_path)
                await message.answer(f"Открываю {app_name}...")
            else:
                await message.answer(f"Приложение {app_name} не найдено.")
        else:
            await message.answer("Пожалуйста, укажите название приложения.")
    except Exception as e:
        logging.error(f"Error: {e}")


# /open_site
@dp.message(Command("open_site"))
async def cmd_open_site(message: Message):
    try:
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            url = args[1]
            # Add the URL to the database
            add_site(url)

            # Open the URL in the default browser
            subprocess.Popen(['start', url], shell=True)

            await message.answer(f"Открываю сайт {url}...")
        else:
            await message.answer("Пожалуйста, укажите URL сайта.")

        # Show the last 5 sites
        last_sites = get_last_sites()
        if last_sites:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=site, url=site)] for site in last_sites
                ]
            )
            await message.answer("Последние открытые сайты:", reply_markup=keyboard)
        else:
            await message.answer("Недавно открытых сайтов нет.")
    except Exception as e:
        logging.error(f"Error: {e}")


async def main():
    logging.basicConfig(level=logging.INFO)
    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logging.error(f"Error: {e}")
            await asyncio.sleep(5)


if __name__ == '__main__':
    asyncio.run(main())
