FROM python:3.11

WORKDIR /backend

ARG ENV_TYPE

ENV ENV_TYPE=${ENV_TYPE} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONBUFFERED=1 \
    POETRY_VERSION=1.3.1

COPY pyproject.toml /backend/

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y default-libmysqlclient-dev
RUN apt-get install -y curl

RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=$POETRY_VERSION python -
ENV PATH /root/.local/bin:$PATH

RUN poetry config virtualenvs.create false 
RUN poetry install $(test "$ENV_TYPE" == production && echo "--no-dev") --no-interaction --no-ansi

COPY . /backend
