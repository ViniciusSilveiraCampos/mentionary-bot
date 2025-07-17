FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip \
    && pip install poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root
COPY ./app.py .
COPY ./.env .

CMD ["python", "app.py"]
