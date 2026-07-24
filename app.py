import os
import random
import threading
import asyncio
from flask import Flask, request, Response
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from groq import Groq

# --- Переменные окружения ---
TOKEN = os.environ["TG_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

ai = Groq(api_key=GROQ_API_KEY)

songs = [
    "Lemon Demon — Ode to Crayola",
    "Lemon Demon — Touch-Tone Telephone",
    "Lemon Demon — Cabinet Man",
    "Lemon Demon — The Ultimate Showdown",
    "Lemon Demon — Two Trucks (вам выпал редкий трек)",
    "Lemon Demon — Fine",
    "Lemon Demon — Lifetime Achievement Award",
    "Lemon Demon — Spiral of Ants",
    "Lemon Demon — Redesign Your Logo",
    "Lemon Demon — Eighth Wonder",
    "Lemon Demon — Marketland",
    "Lemon Demon — Modify",
    "Lemon Demon — Sweet Bod",
    "Lemon Demon — Amnesia Was Her Name",
    "Lemon Demon — Ancient Aliens",
    "Lemon Demon — The Machine"
]

albums = [
    "Spirit Phone",
    "Nature Tapes",
    "Damn Skippy",
    "Hip to the Javabean",
    "Mouth Sounds",
    "Mouth Silence",
]

art_ideas = [
    "Нарисуй Lemon Demon в стиле старого VHS-хоррора с глитчами",
    "Нарисуй своего перса в футболке ЛД",
    "Нарисуй что-то в духе Animutation",
    "Перерисуй обложку любого альбома Lemon Demon",
    "Нарисуй Нила Сичирега в образе персонажа из его клипов",
    "Создай коллаж из кадров разных клипов Lemon Demon"
]

async def song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track = random.choice(songs)
    await update.message.reply_text(f"🎵 Тебе выпал трек:\n\n{track} 🍋")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🍋 Привет! Я Neil Buddy!\n"
        "Я знаю Lemon Demon, Neil Cicierega и его проекты.\n\n"
        "Напиши /help чтобы увидеть команды."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🍋 Команды:\n\n"
        "/song — случайный трек\n"
        "/album — случайный альбом\n"
        "/artidea — идея для арта\n"
        "/lore — факт про Neil\n"
    )

async def album(update: Update, context: ContextTypes.DEFAULT_TYPE):
    picked = random.choice(albums)
    await update.message.reply_text(f"💿 Тебе выпал альбом:\n\nNeil Cicierega — {picked} 🍋")

async def artidea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    picked_idea = random.choice(art_ideas)
    await update.message.reply_text(f"🎨 Идея:\n{picked_idea}")

async def lore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧠 Neil Cicierega — музыкант, аниматор и создатель Lemon Demon. "
        "Известен как создатель серии Potter Puppet Pals, жанра Animutation, "
        "а также различных музыкальных альбомов под именем Lemon Demon и серии mashup-альбомов под своим именем. "
        "Cicierega работал над такими проектами, как New Kids on the Rock, Gravity Falls."
    )

async def handle_response(update: Update, response):
    try:
        await update.message.reply_text(response.choices[0].message.content)
    except Exception as e:
        await update.message.reply_text("Произошла ошибка при обработке запроса 😨⚠️")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        response = ai.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты Neil Buddy 🍋\n\n"
                        "Ты ИИ-друг.\n"
                        "Ты знаешь Neil Cicierega,\n"
                        "Lemon Demon, Spirit Phone,\n"
                        "Mouth albums и другие проекты.\n\n"
                        "Ты дружелюбный и спокойный,\n"
                        "немного хаотичный и странный,\n"
                        "любишь музыку, арты и творчество."
                    )
                },
                {"role": "user", "content": text}
            ]
        )
        await handle_response(update, response)
    except Exception as e:
        await update.message.reply_text("Не удалось получить ответ от ИИ 😨⚠️")

def run_polling_loop():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("song", song))
    app.add_handler(CommandHandler("album", album))
    app.add_handler(CommandHandler("artidea", artidea))
    app.add_handler(CommandHandler("lore", lore))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("🍋 Neil Buddy запущен!")
    app.run_polling()

# --- Flask для «пробуждения» сервиса на Render ---
app_flask = Flask(__name__)

@app_flask.route("/")
def home():
    return "Neil Buddy is alive! 🍋"

@app_flask.route("/health")
def health():
    return Response("OK", status=200)

if __name__ == "__main__":
    # Запускаем polling в отдельном потоке, чтобы Flask мог слушать порт
    threading.Thread(target=run_polling_loop, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app_flask.run(host="0.0.0.0", port=port)