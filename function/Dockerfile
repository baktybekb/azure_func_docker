FROM mcr.microsoft.com/azure-functions/python:4-python3.10

COPY . /home/site/wwwroot
RUN pip install -r /home/site/wwwroot/requirements.txt

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true
