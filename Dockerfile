FROM python:3.8 AS builder

ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

COPY requirements.txt ./

RUN pip install -U pip && \
    pip install --user -r requirements.txt && \
    pip install --user gunicorn

FROM python:3.8-slim

LABEL Maintainer="https://github.com/pacificclimate/osprey" \
    Description="osprey WPS" \
    Vendor="pacificclimate" \
    Version="1.2.1"

WORKDIR /tmp

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY ./osprey /tmp/osprey

EXPOSE 5000
CMD ["gunicorn", "-t 0", "--bind=0.0.0.0:5000", "osprey.wsgi:application"]
