FROM python:3.12

WORKDIR /app

# Создание папки для базы данных и установка прав
RUN mkdir -p /app/db && chmod -R 777 /app/db

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем все файлы приложения в контейнер
COPY . .

# Запустите приложение
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
