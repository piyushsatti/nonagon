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

EXPOSE 8000

CMD ["uvicorn", "nonagon_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
