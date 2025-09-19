from model_handler import FlanT5Model

def test_model():
    model = FlanT5Model()
    test_prompts = [
        "پایتون چیست؟",
        "هوش مصنوعی چه کاربردی دارد؟",
        "چگونه برنامه نویس شوم؟"
    ]
    
    for prompt in test_prompts:
        response = model.generate_response(prompt)
        print(f"سوال: {prompt}")
        print(f"پاسخ: {response}")
        print("-" * 50)

if __name__ == "__main__":
    test_model()
