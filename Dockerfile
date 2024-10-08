FROM python:3.13.0-alpine@sha256:81362dd1ee15848b118895328e56041149e1521310f238ed5b2cdefe674e6dbf

WORKDIR /app

COPY . /app/app-catalog

RUN pip3 install -r app-catalog/requirements.txt

CMD ["python", "-u", "/app/app-catalog/main.py"]