FROM python:3.7-slim

MAINTAINER https://github.com/pacificclimate/osprey
LABEL Description="osprey WPS" Vendor="pacificclimate" Version="0.1.0"

ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

RUN apt-get update && apt-get install -y \
    build-essential

WORKDIR /code

COPY requirements.txt requirements_dev.txt ./

RUN pip install --upgrade pip && \
    pip install -r requirements.txt -r requirements_dev.txt && \
    pip install gunicorn

COPY . .

EXPOSE 5001

CMD ["gunicorn", "--bind=0.0.0.0:5002", "osprey.wsgi:application"]

# docker build -t pacificclimate/osprey .
# docker run -p 5001:5001 pacificclimate/osprey
# http://localhost:5001/wps?request=GetCapabilities&service=WPS
# http://localhost:5001/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
