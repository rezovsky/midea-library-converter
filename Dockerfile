# Используйте базовый образ
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем все файлы приложения в контейнер
COPY . /app

# Укажите рабочую директорию
WORKDIR /app

# Запустите приложение
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
