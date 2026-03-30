
import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# состояния для регистрации
NAME, AGE, CITY = range(3)

# токен бота
BOT_TOKEN = "PASTE_YOUR_TOKEN_HERE"

# настройка логов
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# -------------------------
# работа с базой данных
# -------------------------
def init_db():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        age INTEGER,
        city TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        text TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_user_basic(user):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO users (user_id, username, first_name, age, city)
    VALUES (
        ?,
        ?,
        ?,
        COALESCE((SELECT age FROM users WHERE user_id = ?), NULL),
        COALESCE((SELECT city FROM users WHERE user_id = ?), NULL)
    )
    """, (user.id, user.username, user.first_name, user.id, user.id))

    conn.commit()
    conn.close()


def save_registration(user_id, age, city):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET age = ?, city = ?
    WHERE user_id = ?
    """, (age, city, user_id))

    conn.commit()
    conn.close()


def save_message(user_id, text):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO messages (user_id, text)
    VALUES (?, ?)
    """, (user_id, text))

    conn.commit()
    conn.close()


def get_user_stats(user_id):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM messages WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]

    conn.close()
    return count


# -------------------------
# обработчики команд
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user_basic(user)

    text = (
        f"Привет, {user.first_name}!\n\n"
        "Я учебный Telegram-бот.\n"
        "Команды:\n"
        "/start - запуск\n"
        "/help - помощь\n"
        "/register - регистрация\n"
        "/stats - статистика\n"
        "/options - кнопки"
    )
    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Я умею:\n"
        "1. Отвечать на команды\n"
        "2. Сохранять сообщения в базу данных\n"
        "3. Проводить регистрацию по шагам\n"
        "4. Показывать inline-кнопки"
    )
    await update.message.reply_text(text)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    count = get_user_stats(user.id)
    await update.message.reply_text(f"Вы отправили сообщений: {count}")


# -------------------------
# inline кнопки
# -------------------------
async def options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Опция 1", callback_data="opt1")],
        [InlineKeyboardButton("Опция 2", callback_data="opt2")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите вариант:", reply_markup=reply_markup)


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "opt1":
        await query.edit_message_text("Вы выбрали опцию 1")
    elif query.data == "opt2":
        await query.edit_message_text("Вы выбрали опцию 2")


# -------------------------
# регистрация через состояния
# -------------------------
async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите ваше имя:")
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Введите ваш возраст:")
    return AGE


async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        age = int(update.message.text)
        context.user_data["age"] = age
        await update.message.reply_text("Введите ваш город:")
        return CITY
    except ValueError:
        await update.message.reply_text("Возраст должен быть числом")
        return AGE


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    city = update.message.text
    age = context.user_data["age"]

    save_user_basic(user)
    save_registration(user.id, age, city)

    await update.message.reply_text(
        f"Регистрация завершена!\n"
        f"Имя: {context.user_data['name']}\n"
        f"Возраст: {age}\n"
        f"Город: {city}"
    )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Регистрация отменена")
    return ConversationHandler.END


# -------------------------
# обработка обычных сообщений
# -------------------------
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    save_user_basic(user)
    save_message(user.id, text)

    await update.message.reply_text(f"Вы написали: {text}")


# -------------------------
# обработка ошибок
# -------------------------
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}")


# -------------------------
# запуск приложения
# -------------------------
def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    # обычные команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("options", options))
    app.add_handler(CallbackQueryHandler(button_click))

    # диалог регистрации
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("register", register_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)

    # эхо-сообщения
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # обработчик ошибок
    app.add_error_handler(error_handler)

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
