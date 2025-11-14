<center><img src="https://raw.githubusercontent.com/colav/colav.github.io/master/img/Logo.png"/></center>

# Quyca

ImpactU Backend written in Python with flask, it is used to provide the API for the Colav platform.

# Installation

## Dependencies

Docker and docker-compose is required.

- https://docs.docker.com/engine/install/ubuntu/ (or https://docs.docker.com/engine/install/debian/, etc)
- Install `docker-compose`:

```bash
apt install docker-compose
```

or

```bash
pip install docker-compose
```

- https://docs.docker.com/engine/install/linux-postinstall/

- Deploy Elastic Search from Chia https://github.com/colav/Chia/tree/main/elasticsaerch

To install the package, you can use the following command:

```shell
pip install quyca
```

But this package us deployed with docker, then you need to install docker and docker-compose to run the package.

To deploy you need to edit .env.example file and rename it to:
.env.local to test the code in your local machine.
.env.prod to deploy the code in a production environment.
.env.dev to deploy the code in a development environment.

### Pre-commit

If you dont have pre-commit installed

```bash
poetry add --dev pre-commit
```

Then install the hook in `.pre-commit-config.yaml` in your local repo, using:

```bash
pre-commit install
```

And then you have it.

## Data

Required data is stored in MongoDB, produced with kahi.
usually database named kahi or kahi_dev, please read

# Usage

edit the .env.example renaming it to .env.dev or .env.prod and set the variables.

```bash
APP_NAME=quyca
APP_VERSION=0.0.1
APP_PORT=8010
APP_DOMAIN=localhost:8010
APP_DEBUG=True

APP_URL_PREFIX=/app
API_URL_PREFIX=/api

MONGO_SERVER=localhost
MONGO_USERNAME=
MONGO_PASSWORD=
MONGO_DATABASE=kahi_dev
MONGO_PORT=27017
MONGO_CALCULATIONS_DATABASE=kahi_calculations_dev

#ElasticSearch
ES_SERVER=http://localhost:9200
ES_USERNAME=
ES_PASSWORD=
ES_PERSON_COMPLETER_INDEX=kahi_dev_person
ES_INSTITUTION_COMPLETER_INDEX=kahi_dev_institution
ES_GROUP_COMPLETER_INDEX=kahi_dev_group
ES_DEPARTMENT_COMPLETER_INDEX=kahi_dev_department
ES_FACULTY_COMPLETER_INDEX=kahi_dev_faculty

JWT_SECRET_KEY=123aabbcc
JWT_ACCESS_TOKEN_EXPIRES=3600

LOCAL_STORAGE_PATH=/app # ruta para guardar el archivo si hay problemas con google drive

GOOGLE_CREDENTIALS=/app # ruta para guardar el .pickle

GOOGLE_PARENT_ID= # ID de la carpetade GoogleDrive

API_LIMITS=100000 per day,10 per second

SENTRY_DSN=
```

Please read the Makefile to see the available commands to run the package.
https://github.com/colav/quyca/blob/develop/Makefile

To tests requests to the API, you can use the next urls:

- :8010/app/your/endpoint/here
- :8010/api/your/endpoint/here

where /app is the endpoint for the web application and /api is the endpoint for the expert API.
:8010 is the default port for the application but it can be changed in the .env file.

# Start the application

```bash
make up-dev  # to call "docker-compose up -d" for development
```

or

```bash
make up-prod  # to call "docker-compose up -d" for production
```

## Running tests

```bash
make tests-dev    # to run the tests
```

could be the same for prod with

```bash
make tests-prod    # to run the tests
```

### Format the code

Dependencies:

```shell
pip install black poetry autoflake
```

To format the code, you can use the following command:

```shell
python format.py
```

# List of endpoints

Run the next command to see the list of endpoints

```bash
docker compose  exec dev bash
```

luego dentro del contenedor

```bash
FLASK_APP='app' flask routes
```

# License

BSD-3-Clause License

# Links

http://colav.udea.edu.co/
