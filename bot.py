import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# .env faylini yuklash (lokal muhit uchun)
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("MY_Token")
GEMINI_API_KEY = os.getenv("Google_API_Key")

# Gemini API mijozini sozlash
client = genai.Client(api_key=GEMINI_API_KEY)

# Render platformasi port talab qilgani uchun kichik HTTP server
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active and running!")

    def log_message(self, format, *args):
        # Render loglarini keraksiz so'rovlar bilan to'ldirmaslik uchun
        return

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"HTTP server {port}-portda ishga tushdi...")
    server.serve_forever()

# /start buyrug'i uchun ishlovchi
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "Assalomu alaykum! Men Gemini AI bilan ishlaydigan Telegram botman. Menga xabar yuboring!"
    await update.message.reply_text(welcome_text)

# Xabarlarni qabul qilib Gemini AI ga yuboruvchi ishlovchi
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        # Gemini 3 Flash Preview modeliga so'rov yuborish
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=user_text,
        )
        bot_response = response.text
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")
        bot_response = "Uzr, javob tayyorlashda xatolik yuz berdi."

    await update.message.reply_text(bot_response)

def main():
    # 1. Port xatoligini oldini olish uchun HTTP serverni alohida oqimda ishga tushirish
    threading.Thread(target=run_dummy_server, daemon=True).start()

    # 2. Telegram Bot ilovasini yaratish
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # 3. Handlerlarni ulash
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # 4. Botni ishga tushirish
    print("Bot muvaffaqiyatli ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()