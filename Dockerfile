FROM python:3.11.9-alpine@sha256:f9ce6fe33d9a5499e35c976df16d24ae80f6ef0a28be5433140236c2ca482686

WORKDIR /app

COPY . /app/app-catalog

RUN pip3 install -r app-catalog/requirements.txt

CMD ["python", "-u", "/app/app-catalog/main.py"]