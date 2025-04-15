FROM alpine:latest

RUN apk add python3 uv

WORKDIR /app

COPY . .

RUN uv -n sync --frozen

CMD ["uv", "run", "main.py"]
