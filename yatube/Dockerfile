FROM python:3.11-slim

LABEL description="Yatube" \
      version="1.0" \
      maintainer="TheSuncatcher222" \
      deployer="https://github.com/TheSuncatcher222"

RUN apt-get update && \
    apt-get install -y dos2unix

RUN pip install --upgrade pip

RUN pip install gunicorn==20.1.0

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

RUN dos2unix run_django_not_prod.sh

CMD ["bash", "run_django_not_prod.sh"]
