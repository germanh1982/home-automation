FROM alpine:3.21

RUN apk update
RUN apk add --no-cache \
    python3 \
    py3-pip

WORKDIR /app
COPY REQUIREMENTS .

RUN python3 -m venv .
RUN bin/pip3 install -r REQUIREMENTS

COPY main.py .

CMD ["bin/python3", "main.py", "/run/secrets/config.yml"]
