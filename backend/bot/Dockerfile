FROM python:3.13-slim

WORKDIR /app

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy backend package
COPY backend/ ./backend/

# Install the backend package
RUN uv pip install --system -e backend/

# Create logs directory
RUN mkdir -p /app/logs

CMD ["python", "-m", "nonagon_bot.main"]
