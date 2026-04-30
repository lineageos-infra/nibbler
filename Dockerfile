FROM python:3.11-alpine
RUN apk add --no-cache git protoc redis

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD honcho start
