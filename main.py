
import os
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
DB_PATH = os.getenv("DB_PATH", "movies.db")

def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute("CREATE TABLE IF NOT EXISTS movies (code TEXT PRIMARY KEY, file_id TEXT NOT NULL)")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Kino botga xush kelibsiz!\nKino kodini yuboring.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if update.effective_user.id != ADMIN_ID:
        await msg.reply_text("Bu buyruq faqat admin uchun.")
        return
    code = (msg.caption or "").strip()
    if not msg.video or not code.isdigit():
        await msg.reply_text("Videoga izoh sifatida kino kodini yozing. Masalan: 101")
        return
    with sqlite3.connect(DB_PATH) as db:
        db.execute("INSERT OR REPLACE INTO movies VALUES (?, ?)", (code, msg.video.file_id))
    await msg.reply_text(f"✅ {code} kodi saqlandi!")

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    with sqlite3.connect(DB_PATH) as db:
        row = db.execute("SELECT file_id FROM movies WHERE code = ?", (code,)).fetchone()
    if row:
        await update.message.reply_video(row[0])
    else:
        await update.message.reply_text("❌ Kino topilmadi. Kodni tekshiring.")

def main():
    init_db()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
    app.run_polling()

if __name__ == "__main__":
    main()
