# استخدام نسخة بايثون خفيفة
FROM python:3.9-slim

# تحديد مجلد العمل داخل الحاوية (Container)
WORKDIR /app

# نسخ ملف المكتبات المطلوبة أولاً لسرعة البناء
COPY requirements.txt .

# تثبيت المكتبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات السيرفر إلى داخل الحاوية
COPY . .

# فتح المنفذ 5000 الذي يعمل عليه Flask
EXPOSE 5000

# أمر تشغيل السيرفر
CMD ["python", "license.py"]
