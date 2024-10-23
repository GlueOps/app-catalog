FROM python:3.11.10-alpine@sha256:f089154eb2546de825151b9340a60d39e2ba986ab17aaffca14301b0b961a11c

WORKDIR /app

COPY . /app/app-catalog

RUN pip3 install -r app-catalog/requirements.txt

CMD ["python", "-u", "/app/app-catalog/main.py"]