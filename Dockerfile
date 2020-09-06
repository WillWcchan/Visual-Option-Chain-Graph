# pull base image
FROM python:3.7.9-buster

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# set work directory
WORKDIR /code

# install dependencies
COPY requirements.txt /code/

# https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
RUN pip install --upgrade pip \
    pip install -r requirements.txt

# copy project
COPY . /code/