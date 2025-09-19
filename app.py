import os
import asyncio
from telethon import TelegramClient, events
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
import requests
from io import BytesIO

# تنظیمات ربات
API_ID = '22004807'  # از my.telegram.org دریافت کنید
API_HASH = '1ec7530fc7c4892ebbef7371bb6105ba'  # از my.telegram.org دریافت کنید
BOT_TOKEN = '8352301516:AAG53OQsRiqr7SJ4H4P1O_D3y-KiKEcaDPs'  # از @BotFather دریافت کنید

# آدرس مدل در Google Drive (لینک مستقیم)
MODEL_URL = "https://drive.google.com/uc?export=download&id=YOUR_FILE_ID"

# مسیر ذخیره مدل محلی
MODEL_PATH = "flan-t5-small"

class AIBot:
    def __init__(self):
        self.client = None
        self.model = None
        self.tokenizer = None
        self.model_loaded = False
        
    async def download_model(self):
        """دانلود مدل از Google Drive"""
        if not os.path.exists(MODEL_PATH):
            os.makedirs(MODEL_PATH)
            
            print("در حال دانلود مدل...")
            response = requests.get(MODEL_URL)
            
            if response.status_code == 200:
                # ذخیره مدل
                with open(os.path.join(MODEL_PATH, "pytorch_model.bin"), "wb") as f:
                    f.write(response.content)
                print("مدل دانلود شد.")
            else:
                print("خطا در دانلود مدل. از مدل پیش‌فرض HuggingFace استفاده می‌شود.")
                return False
        return True

    def load_model(self):
        """بارگذاری مدل هوش مصنوعی"""
        try:
            print("در حال بارگذاری مدل...")
            
            # اگر مدل دانلود شده وجود دارد، از آن استفاده کن
            if os.path.exists(MODEL_PATH):
                self.tokenizer = T5Tokenizer.from_pretrained(MODEL_PATH)
                self.model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH)
            else:
                # استفاده از مدل از HuggingFace
                self.tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-small")
                self.model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-small")
            
            print("مدل بارگذاری شد.")
            self.model_loaded = True
            return True
            
        except Exception as e:
            print(f"خطا در بارگذاری مدل: {e}")
            return False

    def generate_response(self, prompt):
        """تولید پاسخ با مدل هوش مصنوعی"""
        if not self.model_loaded:
            return "مدل هوش مصنوعی بارگذاری نشده است."
        
        try:
            # توکنایز کردن ورودی
            input_ids = self.tokenizer.encode(prompt, return_tensors="pt")
            
            # تولید پاسخ
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids,
                    max_length=150,
                    num_beams=5,
                    early_stopping=True,
                    temperature=0.7
                )
            
            # دیکد کردن پاسخ
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response
            
        except Exception as e:
            return f"خطا در پردازش: {str(e)}"

    async def start(self):
        """شروع ربات"""
        # بارگذاری مدل
        self.load_model()
        
        # ایجاد کلینت تلگرام
        self.client = TelegramClient('ai_bot', API_ID, API_HASH)
        
        # تعریف هندلر برای پیام‌ها
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            await event.reply('سلام! من یک ربات هوش مصنوعی هستم. هر پیامی بفرستید تا پاسخ دهم.')
        
        @self.client.on(events.NewMessage)
        async def message_handler(event):
            # اگر پیام از خود ربات باشد، پاسخ نده
            if event.sender_id == (await self.client.get_me()).id:
                return
            
            # نشان دادن تایپ کردن
            async with self.client.action(event.chat_id, 'typing'):
                # تولید پاسخ
                response = self.generate_response(event.text)
                await event.reply(response)
        
        # شروع ربات
        print("ربات در حال اجراست...")
        await self.client.start(bot_token=BOT_TOKEN)
        await self.client.run_until_disconnected()

# اجرای ربات
if __name__ == "__main__":
    bot = AIBot()
    asyncio.run(bot.start())
