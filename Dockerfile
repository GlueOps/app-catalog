FROM python:3.12.7-alpine@sha256:38e179a0f0436c97ecc76bcd378d7293ab3ee79e4b8c440fdc7113670cb6e204

WORKDIR /app

COPY . /app/app-catalog

RUN pip3 install -r app-catalog/requirements.txt

CMD ["python", "-u", "/app/app-catalog/main.py"]