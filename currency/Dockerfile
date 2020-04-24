FROM python:3.6.9-slim-buster

ENV PYTHONUNBUFFERED 1

# Install Apt packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential libpq-dev wget curl vim less && \
    rm -rf /var/lib/apt/lists/*

# Python requirements
COPY . /opt/currency/

RUN rm -rf /opt/currency/static
RUN mkdir -p /opt/currency/static

WORKDIR /opt/currency
RUN pip install -r requirements.txt
