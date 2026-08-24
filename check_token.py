import asyncio
from telegram import Bot
import config

async def check():
    bot = Bot(token=config.TELEGRAM_TOKEN)
    try:
        me = await bot.get_me()
        print(f"✅ Токен работает!")
        print(f"📱 Имя бота: @{me.username}")
        print(f"🆔 ID бота: {me.id}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("🔧 Проверьте токен в config.py")
        print("📌 Получите новый токен у @BotFather")

if __name__ == "__main__":
    asyncio.run(check())