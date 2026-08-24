import logging
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import config
import db
import utils

logging.basicConfig(level=logging.INFO)
db.init_db()

user_moodboards = {}
user_prompts = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    await update.message.reply_text(
        "💅 Добро пожаловать в AI-студию маникюра!\n\n"
        "Отправьте мне:\n"
        "• Текстовое описание (например: 'френч с золотыми листьями')\n"
        "• Или фото-мудборды (до 5 штук) – я выделю цвета и создам дизайн.\n"
        "• Или комбинируйте: текст + фото.\n\n"
        "Команды:\n"
        "/generate - создать дизайн\n"
        "/history - ваши прошлые работы\n"
        "/help - помощь\n\n"
        "⚠️ ПЕРВЫЙ ЗАПУСК МОЖЕТ ЗАНЯТЬ 5-10 МИНУТ (загрузка модели)"
    )

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    tg_id = user.id
    photo_files = []
    
    try:
        if update.message.photo:
            for photo in update.message.photo:
                file = await context.bot.get_file(photo.file_id)
                path = f"temp_{tg_id}_{photo.file_id}.jpg"
                await file.download_to_drive(path)
                photo_files.append(path)
        elif update.message.document and update.message.document.mime_type.startswith('image/'):
            file = await context.bot.get_file(update.message.document.file_id)
            path = f"temp_{tg_id}_{update.message.document.file_id}.jpg"
            await file.download_to_drive(path)
            photo_files.append(path)
        
        if not photo_files:
            await update.message.reply_text("Отправьте изображение или текст.")
            return
        
        if len(photo_files) > 5:
            await update.message.reply_text("Максимум 5 фото.")
            return
        
        user_moodboards[tg_id] = photo_files
        colors = utils.extract_colors(photo_files[0], 5)
        await update.message.reply_text(
            f"📸 Принято {len(photo_files)} фото.\n"
            f"Цвета: {', '.join(colors)}\n"
            f"Теперь введите /generate для создания дизайна"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка загрузки фото: {str(e)}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    text = update.message.text
    if text.startswith('/'):
        return
    user_prompts[tg_id] = text
    await update.message.reply_text(f"✏️ Описание принято: '{text}'\nВведите /generate для создания.")

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from image_gen import generate_image
    
    tg_id = update.effective_user.id
    photo_files = user_moodboards.get(tg_id, [])
    user_prompt = user_prompts.get(tg_id, '')
    
    if not user_prompt and not photo_files:
        await update.message.reply_text("❌ Сначала отправьте описание или фото.")
        return
    
    order_id = db.create_order(tg_id, user_prompt or "без описания")
    status_msg = await update.message.reply_text("🎨 Генерация дизайна... (20-40 секунд)\n⚠️ Первый запуск может быть дольше")
    
    try:
        path = generate_image(user_prompt, photo_files, order_id, tg_id)
        db.update_order_status(order_id, 'generated', path)
        
        with open(path, 'rb') as f:
            await update.message.reply_photo(
                photo=f,
                caption=f"✅ Ваш дизайн готов!\nЗаказ #{order_id}\n\n⬇️ Нажмите на фото и сохраните"
            )
        
        for p in photo_files:
            try: os.remove(p)
            except: pass
        if tg_id in user_moodboards:
            del user_moodboards[tg_id]
        if tg_id in user_prompts:
            del user_prompts[tg_id]
            
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка генерации: {str(e)}\n\nПопробуйте:\n1. Уменьшить количество фото (макс 5)\n2. Упростить текстовое описание\n3. Написать /help для помощи")
    finally:
        await status_msg.delete()

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    orders = db.get_user_orders(tg_id)
    if not orders:
        await update.message.reply_text("📭 У вас пока нет заказов.")
        return
    
    text = "📋 Ваши последние заказы:\n"
    for o in orders[:10]:
        text += f"#{o['id']} | {o['prompt'][:30]}... | {o['status']}\n"
    await update.message.reply_text(text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💅 ПОМОЩЬ:\n\n"
        "1. Отправьте фото (до 5 шт) или текст с описанием\n"
        "2. Введите /generate\n"
        "3. Получите уникальный дизайн маникюра\n\n"
        "Примеры запросов:\n"
        "- 'френч с золотыми листьями'\n"
        "- 'красный матовый с блестками'\n"
        "- 'нежный голубой с цветами'\n\n"
        "⚠️ Если бот не отвечает - подождите, модель загружается"
    )

async def main():
    os.makedirs(config.IMAGES_DIR, exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    print("🔄 Подключение к Telegram API...")
    print("📡 Убедитесь, что VPN включен!")
    
    # Создаем приложение
    app = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    # Добавляем хендлеры
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate_command))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_media))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_media))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    try:
        # Инициализация
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
        bot_info = await app.bot.get_me()
        
        print("🤖 Бот запущен!")
        print(f"📱 Имя бота: @{bot_info.username}")
        print("⚠️ Первый запрос будет долгим (загрузка модели)")
        print("🔄 Нажмите Ctrl+C для остановки")
        
        # Держим бота запущенным
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Остановка бота...")
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n🔧 РЕШЕНИЯ:")
        print("1. Убедитесь, что VPN (Happ 3.3.6) включен")
        print("2. Проверьте интернет-соединение")
        print("3. Проверьте токен бота в config.py")
        print("4. Попробуйте перезапустить бота")

if __name__ == "__main__":
    asyncio.run(main())