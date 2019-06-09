FROM python:3.7.2-slim

COPY ./requirements.txt /

RUN pip install --trusted-host pypi.python.org -r ./requirements.txt

COPY ./app/* /app/

WORKDIR /app

CMD ["python", "app.py"]
