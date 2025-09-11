FROM python:3.11-slim

WORKDIR /app

# نصب dependencies سیستمی مورد نیاز
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# نصب اولیه NumPy و dependencies
RUN pip install numpy==1.24.3
RUN pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
