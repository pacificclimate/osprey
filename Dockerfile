FROM python:3.12-slim AS builder

# Set custom PyPI index URL
ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

# Install Poetry
RUN pip install -U pip && pip install poetry

COPY pyproject.toml poetry.lock ./

ENV POETRY_VIRTUALENVS_CREATE=false

RUN poetry config repositories.pcic https://pypi.pacificclimate.org/simple/ && \
    poetry install

COPY ./osprey /tmp/osprey

FROM python:3.12-slim

LABEL Maintainer="https://github.com/pacificclimate/osprey" \
    Description="osprey WPS" \
    Vendor="pacificclimate" \
    Version="1.2.3"

# Set working directory
WORKDIR /tmp
COPY --from=builder /usr/local /usr/local
COPY ./osprey /tmp/osprey

EXPOSE 5000
CMD ["gunicorn", "-t", "0", "--bind=0.0.0.0:5000", "osprey.wsgi:application"]
