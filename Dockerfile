FROM alpine:latest

RUN apk add --no-cache python3 uv tzdata

WORKDIR /app

COPY uv.lock .
COPY pyproject.toml .

RUN uv -n sync --frozen

COPY . .

RUN echo "#!/usr/bin/env sh" > start && \
    echo "uv run alembic upgrade head" >> start && \
    echo "uv run uvicorn main:app --workers 1 --port 8080 --host 0.0.0.0" >> start && \
    chmod +x start

CMD ["/app/start"]
