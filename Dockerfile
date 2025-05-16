FROM python:3.11.11-alpine@sha256:d5e2fc72296647869f5eeb09e7741088a1841195059de842b05b94cb9d3771bb

WORKDIR /app

COPY . /app/app-catalog

RUN pip3 install -r app-catalog/requirements.txt

CMD ["python", "-u", "/app/app-catalog/main.py"]