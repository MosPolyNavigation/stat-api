FROM alpine:latest

RUN apk add --no-cache python3 uv tzdata

WORKDIR /app

COPY uv.lock .
COPY pyproject.toml .

RUN uv -n sync --frozen

COPY . .

CMD ["uv", "run", "stat-api", "serve"]
