FROM python:3.11.9-alpine@sha256:1bcefb95bd059ea0240d2fe86a994cf13ab7465d00836871cf1649bb2e98fb9f

WORKDIR /app

COPY . /app/app-catalog

RUN pip3 install -r app-catalog/requirements.txt

CMD ["python", "-u", "/app/app-catalog/app/main.py"]