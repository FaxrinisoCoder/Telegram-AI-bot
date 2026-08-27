import os
from dotenv import load_dotenv
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# .env faylidagi o'zgaruvchilarni yuklash
load_dotenv()

TELEGRAM_TOKEN = os.getenv("MY_Token")
GEMINI_KEY = os.getenv("Google_API_Key")

# Google Gemini mijozini ishga tushirish
ai_client = genai.Client(api_key=GEMINI_KEY)

# /start buyrug'i uchun handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! Men sun'iy intellekt asosida ishlaydigan yordamchiman. "
        "Menga xohlagan savolingizni berishingiz mumkin!"
    )

# Foydalanuvchidan kelgan har bir matnli xabarni qayta ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Bot javob tayyorlayotganini bildirish ("typing..." effekti)
    await update.message.chat.send_action(action="typing")

    try:
        # Gemini modeliga so'rov yuborish (Google AI Studio dagi model nomi)
        response = ai_client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=user_text,
        )
        reply = response.text
    except Exception as e:
        # Terminalda aniq xatolikni chiqarish (sozlash uchun yordam beradi)
        print(f"Xatolik yuz berdi: {e}")
        reply = "Kechirasiz, javob tayyorlashda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring."

    await update.message.reply_text(reply)

if __name__ == '__main__':
    # Telegram Bot ilovasini yaratish
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Buyruq va xabar handlerlarini ro'yxatdan o'tkazish
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot muvaffaqiyatli ishga tushdi...")
    app.run_polling()