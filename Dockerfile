FROM golang:1.23.1-alpine as overmind
RUN GO111MODULE=on go install github.com/DarthSim/overmind/v2@latest

FROM python:3.11-alpine
COPY --from=overmind /go/bin/overmind /usr/local/bin/overmind

RUN apk add --no-cache curl build-base tmux redis git protoc
RUN curl -L https://github.com/oliver006/redis_exporter/releases/download/v1.31.4/redis_exporter-v1.31.4.linux-amd64.tar.gz -o exporter.tgz \
  && tar xvzf exporter.tgz \
  && cp redis_exporter-*/redis_exporter /usr/local/bin/redis_exporter \
  && rm -rf *exporter*

COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

COPY . /app

CMD /usr/local/bin/overmind start
