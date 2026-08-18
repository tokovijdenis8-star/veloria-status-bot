import os
import asyncio
import threading

from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from mcstatus import JavaServer


MC_HOST = "65.108.6.120"
MC_PORT = 2431


# -------------------------
# Web server for Render
# -------------------------

web = Flask(__name__)


@web.route("/")
def home():
    return "VELORIA Status Bot is running!"


@web.route("/health")
def health():
    return "OK"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)


# -------------------------
# Minecraft status
# -------------------------

def get_server_status():
    try:
        server = JavaServer.lookup(f"{MC_HOST}:{MC_PORT}")
        status = server.status()

        online = status.players.online
        maximum = status.players.max
        version = status.version.name
        latency = round(status.latency)

        return (
            "🎮 VELORIA\n\n"
            "🟢 Сервер онлайн\n"
            f"👥 Игроки: {online}/{maximum}\n"
            f"📡 Пинг: {latency} ms\n"
            f"⚙️ Версия: {version}\n\n"
            f"🌍 IP: {MC_HOST}:{MC_PORT}"
        )

    except Exception:
        return (
            "🎮 VELORIA\n\n"
            "🔴 Сервер офлайн или недоступен\n\n"
            f"🌍 IP: {MC_HOST}:{MC_PORT}"
        )


# -------------------------
# Telegram commands
# -------------------------

async def online(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = await asyncio.to_thread(get_server_status)
    await update.message.reply_text(message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 VELORIA\n\n"
        "Команды:\n"
        "/online — онлайн сервера"
    )


# -------------------------
# Start bot
# -------------------------

def main():
    token = os.environ.get("BOT_TOKEN")

    if not token:
        raise RuntimeError("BOT_TOKEN не задан")

    # Start Render web server
    threading.Thread(target=run_web, daemon=True).start()

    # Start Telegram bot
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("online", online))

    print("VELORIA Status Bot запущен")

    app.run_polling()


if __name__ == "__main__":
    main()