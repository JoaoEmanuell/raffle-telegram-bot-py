FROM python:3.11-alpine

RUN pip install --upgrade pip

# Create no root user

RUN apk add bash && apk add shadow

ENV NO_ROOT_USER=python
ENV NO_ROOT_USER_PASSWORD=python

RUN useradd -m $NO_ROOT_USER

RUN echo "$NO_ROOT_USER:$NO_ROOT_USER_PASSWORD" | chpasswd

# Set user and workdir

USER $NO_ROOT_USER

WORKDIR /usr/src/app

# Config no root env

ENV HOME="/home/python"

ENV PATH="$PATH:$HOME/.local/bin"

# Install requirements

COPY raffle_telegram_bot/requirements.txt .

RUN pip install -r requirements.txt

# Ports and run

EXPOSE 8000

CMD tail -f /dev/null