# Dockerfile
FROM mcr.microsoft.com/azure-functions/python:4-python3.9

COPY . /home/site/wwwroot
RUN pip install --upgrade pip
RUN pip install -r /home/site/wwwroot/requirements.txt

CMD [ "func:host:local" ]
