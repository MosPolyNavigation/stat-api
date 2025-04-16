FROM alpine:latest

RUN apk add --no-cache python3 uv tzdata

WORKDIR /app

COPY . .

RUN echo "#!/usr/bin/env sh" > start && \
    echo "uv run alembic upgrade head" >> start && \
    echo "uv run uvicorn main:app --workers 2 --port 8080 --host 0.0.0.0" >> start && \
    chmod +x start

RUN uv -n sync --frozen

CMD ["/app/start"]
