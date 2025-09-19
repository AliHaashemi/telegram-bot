import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from model_handler import FlanT5Model
from database import SupabaseDB

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("توکن ربات تلگرام تنظیم نشده است!")
        
        self.model = FlanT5Model()
        self.db = SupabaseDB()
        self.application = Application.builder().token(self.token).build()
        
        # ثبت هندلرها
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # مدیریت خطا
        self.application.add_error_handler(self.error_handler)
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """هندلر دستور /start"""
        user = update.effective_user
        welcome_message = (
            f"سلام {user.first_name}! 👋\n\n"
            "من یک ربات هوش مصنوعی هستم که از مدل **FLAN-T5-Base** استفاده می‌کنم. "
            "می‌تونی هر سوالی داری از من بپرسی و من سعی می‌کنم بهترین پاسخ رو بهت بدم.\n\n"
            "از دستور /help برای دریافت راهنما استفاده کن."
        )
        await update.message.reply_text(welcome_message)
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """هندلر دستور /help"""
        help_message = (
            "🤖 راهنمای ربات (FLAN-T5-Base):\n\n"
            "• فقط پیام خودت رو بفرست و من بهش پاسخ میدم\n"
            "• می‌تونی در مورد هر موضوعی از من سوال بپرسی\n"
            "• من از مدل **Google FLAN-T5-Base** برای تولید پاسخ استفاده می‌کنم\n"
            "• مکالمات ما در دیتابیس ذخیره میشن\n\n"
            "همین الآن می‌تونی سوالت رو بپرسی!"
        )
        await update.message.reply_text(help_message)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """هندلر پیام‌های متنی"""
        user_id = update.effective_user.id
        user_message = update.message.text
        
        # نشان دادن وضعیت تایپینگ
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # استفاده از executor برای جلوگیری از блок کردن event loop
            loop = asyncio.get_event_loop()
            bot_response = await loop.run_in_executor(
                None, 
                self.model.generate_response, 
                user_message
            )
            
            # ذخیره در دیتابیس
            try:
                self.db.save_conversation(user_id, user_message, bot_response)
            except Exception as e:
                logger.error(f"خطا در ذخیره‌سازی دیتابیس: {e}")
            
            # ارسال پاسخ به کاربر
            await update.message.reply_text(bot_response)
            
        except Exception as e:
            logger.error(f"خطا در پردازش پیام: {e}")
            await update.message.reply_text("متأسفانه در پردازش درخواست شما خطایی رخ داد.")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت خطاهای全局"""
        logger.error(f"خطا رخ داد: {context.error}")
    
    def run(self):
        """اجرای ربات"""
        logger.info("ربات در حال راه‌اندازی...")
        self.application.run_polling()

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()
