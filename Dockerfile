FROM python:3.11.7-slim

WORKDIR /code
RUN pip install --upgrade pip && pip install poetry

# Avoid existing bug where poetry installs dependencies into a wrong directory:
RUN poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml ./
RUN poetry install
COPY ./ ./

ENTRYPOINT ["python", "./heraldecho/main.py"]
