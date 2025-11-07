import os
import logging
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import google.generativeai as genai
import random

# تنظیم لاگ برای خطاها
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# بارگذاری متغیرها از فایل .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# پیکربندی Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# لیست کارت‌های تاروت
TAROT_CARDS = [
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
    "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
    "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
    "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"
]

# گرفتن عکس تصادفی از اینترنت برای هر کارت
def get_tarot_image(card_name):
    return f"https://source.unsplash.com/600x400/?tarot,{card_name.replace(' ', '%20')}"

# --- دستورات ربات ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔮 فال تاروت", callback_data="tarot")],
        [InlineKeyboardButton("📜 فال حافظ", callback_data="hafez")]
    ]
    await update.message.reply_text(
        "سلام به ربات فال تاروت و حافظ خوش اومدی 🌙✨\nیکی از گزینه‌های زیر رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# --- فال تاروت ---
async def tarot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_cards = random.sample(TAROT_CARDS, 3)
    cards_text = "\n".join([f"• {card}" for card in selected_cards])

    prompt = f"""
    کارت‌های تاروت انتخاب شده: {', '.join(selected_cards)}
    برای هر کارت در یک خط، تعبیر کوتاه و روان بنویس (به فارسی).
    در پایان، در ۷ خط خلاصه‌ای زیبا و شاعرانه از معنای کلی فال بنویس.
    """

    response = model.generate_content(prompt)
    text = response.text.strip()

    for card in selected_cards:
        await query.message.reply_photo(
            photo=get_tarot_image(card),
            caption=f"✨ کارت: {card}"
        )

    await query.message.reply_text(f"📖 تعبیر فال:\n{text}\n\n@HafezTarootBot 🌙")

# --- فال حافظ ---
async def hafez_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    prompt = """
    یک غزل تصادفی از حافظ بنویس همراه با تعبیر کوتاه و شاعرانه به فارسی.
    تعبیر در ۵ تا ۷ خط باشد.
    """
    response = model.generate_content(prompt)
    await query.message.reply_text(f"💠 {response.text.strip()}\n\n@HafezTarootBot 🌙")

# --- اجرای ربات ---
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(tarot_handler, pattern="tarot"))
    app.add_handler(CallbackQueryHandler(hafez_handler, pattern="hafez"))
    app.run_polling()

if __name__ == "__main__":
    main()
