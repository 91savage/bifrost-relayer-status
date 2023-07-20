FROM python:3.11-alpine

RUN mkdir -p /app && apk update && apk add gcc libc-dev
WORKDIR /app
COPY relayer_alert.py unbonding.py poetry.lock pyproject.toml ./
COPY . .
RUN pip3 install poetry && poetry config virtualenvs.create false
RUN poetry install --no-dev
CMD ["python3", "relayer_alert.py"]


