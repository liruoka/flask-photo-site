# Используем официальный Python образ
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Экспонируем порт (Flask по умолчанию работает на порту 5000)
EXPOSE 8080

# Команда для запуска Flask приложения
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]