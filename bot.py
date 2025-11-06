import os
import random
import openai
import asyncio
import logging
import sys
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# تنظیمات لاگ‌نویسی
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# بارگذاری متغیرهای محیطی
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# بررسی وجود توکن
if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    logger.error("لطفاً فایل .env را ایجاد کرده و توکن‌های مورد نیاز را وارد کنید")
    sys.exit(1)

openai.api_key = OPENAI_API_KEY

# لیست کارت‌ها برای تاروت
tarot_images = [
    "https://upload.wikimedia.org/wikipedia/en/9/9b/RWS_Tarot_08_Strength.jpg",
    "https://upload.wikimedia.org/wikipedia/en/d/db/RWS_Tarot_16_Tower.jpg",
    "https://upload.wikimedia.org/wikipedia/en/5/53/RWS_Tarot_06_Lovers.jpg",
    "https://upload.wikimedia.org/wikipedia/en/d/d4/RWS_Tarot_19_Sun.jpg",
    "https://upload.wikimedia.org/wikipedia/en/f/f7/RWS_Tarot_10_Wheel_of_Fortune.jpg",
    "https://upload.wikimedia.org/wikipedia/en/f/f5/RWS_Tarot_17_Star.jpg"
]

# پاسخ هوش مصنوعی
def ai_response_sync(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.8
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"خطا در دریافت پاسخ از OpenAI: {e}")
        return "متأسفانه در دریافت پاسخ از هوش مصنوعی مشکلی پیش آمد. لطفاً مجدداً تلاش کنید."

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔮 فال حافظ", callback_data="hafez")],
        [InlineKeyboardButton("🃏 تاروت ۳ کارت", callback_data="tarot3"),
         InlineKeyboardButton("🌟 تاروت ۵ کارت", callback_data="tarot5")]
    ]
    await update.message.reply_text(
        "سلام فرفری 😍✨\nمن ربات فال هوشمندم! انتخاب کن ببین چی در انتظارت هست 💫",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# هندل انتخاب فال
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "hafez":
        prompt = """یک غزل حافظ بنویس و در پایان، 
        یک تفسیر احساسی و خودمانی در ۵ خط بده. 
        با لحن دل‌گرم و شاعرانه، پر از ایموجی ❤️🌙✨"""
        image_url = "https://upload.wikimedia.org/wikipedia/commons/7/7a/Hafez_Tomb_02.jpg"

    elif query.data == "tarot3":
        prompt = """یک فال تاروت ۳ کارتی بنویس. 
        نام هر کارت + معنی کلی + تفسیر ۷ خطی احساسی و مثبت بده.
        متن باید صمیمی و پر از ایموجی باشه 💫💖🃏"""
        image_url = random.choice(tarot_images)

    elif query.data == "tarot5":
        prompt = """یک فال تاروت ۵ کارتی بنویس. 
        هر کارت و معنی‌اش را همراه با تفسیر ۷ خطی احساسی، عاشقانه و پرانرژی بنویس 🌟💌✨"""
        image_url = random.choice(tarot_images)
    else:
        prompt = "یک فال عمومی زیبا و مثبت بنویس 🌞✨"
        image_url = random.choice(tarot_images)

    # نمایش پیام "در حال پردازش"
    await query.edit_message_text("منتظر بمانید، در حال آماده‌سازی فال شما هستم... ✨")
    
    # استفاده از تابع همگام برای دریافت پاسخ
    response_text = ai_response_sync(prompt)

    # ارسال عکس و فال
    try:
        await query.message.reply_photo(
            photo=image_url,
            caption=response_text[:1024],  # محدودیت طول پیام تلگرام
        )
        # حذف پیام "در حال پردازش"
        await query.delete_message()
    except Exception as e:
        logger.error(f"خطا در ارسال پاسخ: {e}")
        await query.edit_message_text("متأسفانه در ارسال پاسخ مشکلی پیش آمد. لطفاً مجدداً تلاش کنید.")

# اجرای ربات
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    
    logger.info("ربات در حال اجراست...")

    try:
        app.run_polling()
    except RuntimeError as e:
        if "no current event loop" in str(e):
            # استفاده از رویکرد جایگزین برای سازگاری با پایتون 3.14+
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(app.initialize())
            loop.create_task(app.updater.start_polling())
            loop.run_forever()
        else:
            raise

if __name__ == "__main__":
    main()