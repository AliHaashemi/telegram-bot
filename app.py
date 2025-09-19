import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
from google.colab import drive

# اتصال به Google Drive
drive.mount('/content/drive')

# مسیر مدل در Google Drive
model_path = '/content/drive/MyDrive/flan-t5-small'

# بارگذاری مدل و توکنایزر
try:
    tokenizer = T5Tokenizer.from_pretrained(model_path)
    model = T5ForConditionalGeneration.from_pretrained(model_path)
    print("مدل با موفقیت بارگذاری شد!")
except Exception as e:
    print(f"خطا در بارگذاری مدل: {e}")

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# توکن ربات تلگرام
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# دستور start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! من یک ربات هوش مصنوعی هستم. هر سوالی داری بپرس."
    )

# پردازش پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    try:
        # تولید پاسخ با مدل
        input_ids = tokenizer.encode(user_message, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                input_ids,
                max_length=150,
                num_beams=5,
                early_stopping=True
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logging.error(f"خطا: {e}")
        await update.message.reply_text("متاسفانه خطایی رخ داد.")

# مدیریت خطا
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.warning(f'Update {update} caused error {context.error}')

# تابع اصلی
def main():
    # ایجاد اپلیکیشن
    app = Application.builder().token(TOKEN).build()
    
    # اضافه کردن handlerها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # مدیریت خطا
    app.add_error_handler(error)
    
    # شروع ربات
    print("ربات در حال اجراست...")
    app.run_polling()

if __name__ == '__main__':
    main()
