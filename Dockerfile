# Используем официальный образ Python
FROM mcr.microsoft.com/azure-functions/python:4-python3.10

# Устанавливаем рабочую директорию
WORKDIR /home/site/wwwroot

# Копируем все файлы в рабочую директорию
COPY . .

# Устанавливаем зависимости
RUN pip install --upgrade pip \
    && pip install -r requirements.txt
