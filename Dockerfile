FROM python:3.13-slim AS base

WORKDIR /app

ENV \ 
	PIP_NO_CACHE_DIR=off \ 
	PIP_DISABLE_PIP_VERSION_CHECK=on \ 
	PYTHONDONTWRITEBYTECODE=1 \ 
	PYTHONUNBUFFERED=1 \ 
	VIRTUAL_ENV=/venv 

ENV \ 
	POETRY_VIRTUALENVS_CREATE=false \ 
	POETRY_VIRTUALENVS_IN_PROJECT=false \ 
	POETRY_NO_INTERACTION=1 \ 
	POETRY_VERSION=2.5.1

# install poetry 
RUN pip install "poetry==$POETRY_VERSION" 

# copy requirements 
COPY pyproject.toml poetry.lock ./ 

# add venv to path 
ENV PATH="$VIRTUAL_ENV/bin:$PATH" 

# Install python packages 
RUN python -m venv $VIRTUAL_ENV \ 
	&& . $VIRTUAL_ENV/bin/activate \ 
	&& poetry install --no-root 

COPY . . 

RUN poetry install 

FROM base AS development 
ENV ENVIRONMENT=dev 

FROM base AS production 
ENV ENVIRONMENT=prod

FROM base AS local 
ENV ENVIRONMENT=local