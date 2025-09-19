import os
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

class FlanT5Model:
    def __init__(self):
        self.model_name = "google/flan-t5-base"
        self.tokenizer = None
        self.model = None
        self.load_model()
    
    def load_model(self):
        """لود مدل از HuggingFace یا کش"""
        try:
            self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(
                self.model_name, 
                device_map="auto",
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True
            )
            print("مدل با موفقیت لود شد")
        except Exception as e:
            print(f"خطا در لود مدل: {e}")
    
    def generate_response(self, prompt: str, max_length: int = 512) -> str:
        """تولید پاسخ با مدل Flan-T5"""
        if not self.model or not self.tokenizer:
            return "مدل در دسترس نیست. لطفاً稍后再试。"
        
        try:
            input_ids = self.tokenizer.encode(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids,
                    max_length=max_length,
                    num_beams=4,
                    early_stopping=True,
                    temperature=0.7
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response
        except Exception as e:
            print(f"خطا در تولید پاسخ: {e}")
            return "خطا در پردازش درخواست شما."
