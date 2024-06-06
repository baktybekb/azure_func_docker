FROM mcr.microsoft.com/azure-functions/python:4-python3.10

# Установите зависимости
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# Копируйте исходный код
COPY . /home/site/wwwroot
