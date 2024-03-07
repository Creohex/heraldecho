FROM python:3.11.7-slim

WORKDIR /code
RUN pip install --upgrade pip && pip install poetry

# avoid existing bug where poetry install dependencies in a wrong place:
RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml ./
RUN poetry install
COPY ./ ./

ENTRYPOINT ["python", "./heraldecho/main.py"]
