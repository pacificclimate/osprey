FROM python:3.7-slim AS builder

ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

# Update system
RUN apt-get update && apt-get install -y \
    build-essential

COPY . /opt/wps

WORKDIR /opt/wps

RUN pip install --upgrade pip && \
    pip install --user . && \
    pip install gunicorn

# vim:set ft=dockerfile:
FROM python:3.7-slim AS prod
MAINTAINER https://github.com/pacificclimate/osprey
LABEL Description="osprey WPS" Vendor="pacificclimate" Version="0.1.0"

COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable:
ENV PATH=/root/.local/bin:$PATH

WORKDIR /opt/wps
COPY . .

EXPOSE 5000
CMD ["gunicorn", "--bind=0.0.0.0:5000", "osprey.wsgi:application"]

# docker build -t pcic/osprey .
# docker run -p 5000:5000 pcic/osprey
# http://localhost:5000/wps?request=GetCapabilities&service=WPS
# http://localhost:5000/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
