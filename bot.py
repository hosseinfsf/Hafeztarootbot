import os
import random
import asyncio
import logging
from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# بارگذاری متغیرهای محیطی
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# بررسی وجود توکن‌ها
if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    logger.error("❌ لطفاً فایل .env را با توکن‌های موردنیاز پر کنید.")
    exit(1)

# راه‌اندازی OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# لیست کارت‌های تاروت
tarot_images = [
    "https://upload.wikimedia.org/wikipedia/en/9/9b/RWS_Tarot_08_Strength.jpg",
    "https://upload.wikimedia.org/wikipedia/en/d/db/RWS_Tarot_16_Tower.jpg",
    "https://upload.wikimedia.org/wikipedia/en/5/53/RWS_Tarot_06_Lovers.jpg",
    "https://upload.wikimedia.org/wikipedia/en/d/d4/RWS_Tarot_19_Sun.jpg",
    "https://upload.wikimedia.org/wikipedia/en/f/f7/RWS_Tarot_10_Wheel_of_Fortune.jpg",
    "https://upload.wikimedia.org/wikipedia/en/f/f5/RWS_Tarot_17_Star.jpg"
]

# دریافت پاسخ از هوش مصنوعی
def ai_response_sync(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # اگر اکانت GPT-4 داری، می‌تونی gpt-4o-mini بذاری
            messages=[
                {"role": "system", "content": "تو یک فالگیر باستانی هستی که تعبیر کارت‌های تاروت را شاعرانه و عمیق بیان می‌کنی."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.9
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"خطا در OpenAI: {e}")
        return "متأسفم، در تعبیر فال مشکلی پیش آمد 🌧️"

# فرمان شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔮 کارت فال من", callback_data="tarot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! من فال‌گیر حافظ تاروت هستم 🧿\nروی دکمه زیر بزن تا کارتت رو بکشم:",
        reply_markup=reply_markup
    )

# هندلر برای کارت فال
async def tarot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    image_url = random.choice(tarot_images)
    prompt = f"تعبیر کارت تاروت زیر را بنویس:\n{image_url}"
    loop = asyncio.get_event_loop()
    ai_text = await loop.run_in_executor(None, ai_response_sync, prompt)
    await query.message.reply_photo(photo=image_url, caption=ai_text)

# مدیریت خطاها
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="⚠️ خطا در ربات:", exc_info=context.error)

# تابع اصلی
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
<<<<<<< HEAD
    app.add_handler(CallbackQueryHandler(tarot))
    app.add_error_handler(error_handler)
    logger.info("✨ ربات در حال اجراست...")
    app.run_polling()
=======
    app.add_handler(CallbackQueryHandler(tarot))
    app.add_error_handler(error_handler)
    logger.info("✨ ربات در حال اجراست...")
    app.run_polling()
>>>>>>> 38c36e360a73d62535d18b89d386df03749528be

if __name__ == "__main__":
    main()
