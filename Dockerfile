FROM python:3.10-slim AS base

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
	POETRY_VERSION=1.8.3 

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

# Install Node.js for apidoc generation - Development 
FROM node:20-slim AS apidoc-builder-dev 

# Install apidoc globally 
RUN npm install -g apidoc 

WORKDIR /app 
COPY . . 

# Generate the API documentation for development 
RUN apidoc -i ./quyca/application/ -o ./quyca/application/static/ -c quyca/application/docs/apidoc.dev.json 

# Stage for apidoc generation - Production
FROM node:20-slim AS apidoc-builder-prod

RUN npm install -g apidoc

WORKDIR /app
COPY . .

# Generate the API documentation for production
RUN apidoc -i ./quyca/application/ -o ./quyca/application/static/ -c quyca/application/docs/apidoc.prod.json

FROM base AS development 
ENV ENVIRONMENT=dev 
COPY --from=apidoc-builder-dev /app/quyca/application/static/ ./quyca/application/static/

FROM base AS production 
ENV ENVIRONMENT=prod
COPY --from=apidoc-builder-prod /app/quyca/application/static/ ./quyca/application/static/

FROM base AS local 
ENV ENVIRONMENT=local