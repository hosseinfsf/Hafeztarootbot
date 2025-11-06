import os
import random
import asyncio
import logging
from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

# ──────────────────────────────
# تنظیمات اولیه
# ──────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    logger.error("❌ لطفاً فایل .env را با توکن‌های لازم پر کنید.")
    exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

# ──────────────────────────────
# لیست کارت‌های تاروت (مثال)
# ──────────────────────────────
tarot_cards = [
    ("The Fool", "https://upload.wikimedia.org/wikipedia/en/9/90/RWS_Tarot_00_Fool.jpg"),
    ("The Magician", "https://upload.wikimedia.org/wikipedia/en/d/de/RWS_Tarot_01_Magician.jpg"),
    ("The High Priestess", "https://upload.wikimedia.org/wikipedia/en/8/88/RWS_Tarot_02_High_Priestess.jpg"),
    ("The Empress", "https://upload.wikimedia.org/wikipedia/en/d/d2/RWS_Tarot_03_Empress.jpg"),
    ("The Lovers", "https://upload.wikimedia.org/wikipedia/en/5/53/RWS_Tarot_06_Lovers.jpg"),
    ("The Hermit", "https://upload.wikimedia.org/wikipedia/en/4/4d/RWS_Tarot_09_Hermit.jpg"),
    ("The Wheel of Fortune", "https://upload.wikimedia.org/wikipedia/en/f/f7/RWS_Tarot_10_Wheel_of_Fortune.jpg"),
    ("The Tower", "https://upload.wikimedia.org/wikipedia/en/d/db/RWS_Tarot_16_Tower.jpg"),
    ("The Star", "https://upload.wikimedia.org/wikipedia/en/f/f5/RWS_Tarot_17_Star.jpg"),
    ("The Sun", "https://upload.wikimedia.org/wikipedia/en/d/d4/RWS_Tarot_19_Sun.jpg")
]

# ──────────────────────────────
# تابع ارتباط با هوش مصنوعی
# ──────────────────────────────
def ai_response_sync(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "تو یک فالگیر باستانی هستی که به زیبایی و شاعرانه فال‌ها را تفسیر می‌کنی."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"⚠️ خطا در ارتباط با OpenAI: {e}")
        return "در تعبیر فال مشکلی پیش آمد 🌧️"

# ──────────────────────────────
# فرمان /start
# ──────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔮 فال تاروت سه کارتی", callback_data="tarot_3")],
        [InlineKeyboardButton("🧿 فال تاروت پنج کارتی", callback_data="tarot_5")],
        [InlineKeyboardButton("📜 فال حافظ", callback_data="hafez")],
        [InlineKeyboardButton("🌐 فال‌های وب اپ", url="https://your-webapp-url.com")]  # بعداً جایگزین می‌کنیم
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام 🌸\nمن فرفری فال‌گیر هستم، مفسر اسرار حافظ و کارت‌های تاروت.\nیکی از گزینه‌های زیر را انتخاب کن:",
        reply_markup=reply_markup
    )

# ──────────────────────────────
# هندلر برای دکمه‌ها
# ──────────────────────────────
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice.startswith("tarot"):
        count = 3 if "3" in choice else 5
        cards = random.sample(tarot_cards, count)

        msg_parts = []
        prompt = f"تعبیر شاعرانه و دقیق کارت‌های زیر را بنویس. برای هر کارت دو خط توضیح بده و در آخر جمع‌بندی کلی حدود ۷ خط بنویس:\n\n"
        for name, img in cards:
            prompt += f"- {name}\n"

        loop = asyncio.get_event_loop()
        ai_text = await loop.run_in_executor(None, ai_response_sync, prompt)

        # ارسال کارت‌ها با توضیح کوتاه
        for name, img in cards:
            await query.message.reply_photo(photo=img, caption=f"✨ {name}")

        await query.message.reply_text(f"🧙‍♀️ تفسیر فرفری:\n\n{ai_text}\n\n@HafezTarootBot")

    elif choice == "hafez":
        poems = [
            "دل می‌رود ز دستم صاحب دلان خدا را...",
            "الا یا ایها الساقی ادر کاساً و ناولها...",
            "اگر آن ترک شیرازی به دست آرد دل ما را..."
        ]
        poem = random.choice(poems)
        prompt = f"تعبیر عرفانی و شاعرانه‌ی این شعر از حافظ را بنویس:\n{poem}"

        loop = asyncio.get_event_loop()
        ai_text = await loop.run_in_executor(None, ai_response_sync, prompt)

        await query.message.reply_photo(
            photo="https://upload.wikimedia.org/wikipedia/commons/3/3a/Hafez_Tomb_2.jpg",
            caption=f"📜 {poem}\n\n{ai_text}\n\n@HafezTarootBot"
        )

# ──────────────────────────────
# مدیریت خطا
# ──────────────────────────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="⚠️ خطا در ربات:", exc_info=context.error)

# ──────────────────────────────
# اجرای اصلی ربات
# ──────────────────────────────
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_error_handler(error_handler)

    logger.info("🤖 ربات در حال اجراست...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == "__main__":
    asyncio.run(main())