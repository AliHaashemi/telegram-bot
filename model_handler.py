import os
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
import logging

logger = logging.getLogger(__name__)

class FlanT5Model:
    def __init__(self):
        self.model_name = "google/flan-t5-base"
        self.tokenizer = None
        self.model = None
        self.load_model()
    
    def load_model(self):
        """لود مدل Flan-T5-Base با بهینه‌سازی برای Railway"""
        try:
            logger.info("در حال لود کردن توکنایزر...")
            self.tokenizer = T5Tokenizer.from_pretrained(
                self.model_name,
                cache_dir="./model_cache"
            )
            
            logger.info("در حال لود کردن مدل...")
            self.model = T5ForConditionalGeneration.from_pretrained(
                self.model_name,
                device_map="auto",
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
                cache_dir="./model_cache"
            )
            
            logger.info("مدل flan-t5-base با موفقیت لود شد")
            
        except Exception as e:
            logger.error(f"خطا در لود مدل: {e}")
            raise e
    
    def generate_response(self, prompt: str, max_length: int = 512) -> str:
        """تولید پاسخ با مدل Flan-T5-Base"""
        if not self.model or not self.tokenizer:
            return "مدل در دسترس نیست. لطفاً稍后再试。"
        
        try:
            # ساخت prompt بهینه برای FLAN-T5
            formatted_prompt = f"پاسخ به این سوال را بده: {prompt}"
            
            input_ids = self.tokenizer.encode(
                formatted_prompt, 
                return_tensors="pt",
                max_length=512,
                truncation=True
            )
            
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids,
                    max_length=max_length,
                    num_beams=4,
                    early_stopping=True,
                    temperature=0.7,
                    repetition_penalty=1.1,
                    do_sample=True
                )
            
            response = self.tokenizer.decode(
                outputs[0], 
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )
            
            return response
            
        except Exception as e:
            logger.error(f"خطا در تولید پاسخ: {e}")
            return "خطا در پردازش درخواست شما."
