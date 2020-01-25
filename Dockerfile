FROM debian:10-slim
MAINTAINER Ramsey Zeitoun

# Install dependencies
RUN apt-get update &&\
    apt install -y \
        build-essential \
        zlib1g-dev \
        libncurses5-dev \
        libgdbm-dev \
        libnss3-dev \
        libssl-dev \
        libreadline-dev \
        libffi-dev \
        wget

# Install Python 3.7.4
RUN cd usr/src &&\
    wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz &&\
    tar -xf Python-3.7.4.tgz &&\
    cd Python-3.7.4 &&\
    ./configure &&\
    make && \
    make altinstall

# Get pip and pip-env
RUN apt install -y python3-pip &&\
    pip3 install pipenv

# Add application to app folder and install environment
COPY . /app
RUN cd /app &&\
    pipenv install --dev --ignore-pipfile

# Run tests
WORKDIR /app