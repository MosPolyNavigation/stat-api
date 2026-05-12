FROM alpine:latest

RUN apk add --no-cache python3 uv tzdata

WORKDIR /app

COPY uv.lock .
COPY pyproject.toml .

RUN uv -n sync --frozen

COPY . .

RUN echo "#!/usr/bin/env sh" > start && \
    echo "uv run stat-api db migrate upgrade head" >> start && \
    echo "uv run stat-api serve" >> start && \
    chmod +x start

CMD ["/app/start"]
