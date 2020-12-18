# vim:set ft=dockerfile:
FROM python:3.7-slim
MAINTAINER https://github.com/pacificclimate/osprey
LABEL Description="osprey WPS" Vendor="pacificclimate" Version="0.1.0"

ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

# Update system
RUN apt-get update && apt-get install -y \
    build-essential

COPY . /opt/wps

WORKDIR /opt/wps

RUN pip install --upgrade pip && \
    pip install -e .

EXPOSE 5000
ENTRYPOINT ["sh", "-c"]
CMD ["exec osprey start -b 0.0.0.0"]

# docker build -t pcic/osprey .
# docker run -p 5000:5000 pcic/osprey
# http://localhost:5000/wps?request=GetCapabilities&service=WPS
# http://localhost:5000/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
