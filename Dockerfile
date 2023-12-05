FROM python:3.11-alpine

RUN pip install --upgrade pip

WORKDIR /usr/src/app

COPY raffle_telegram_bot .

# Install requirements

RUN pip install -r requirements.txt

# Ports and run

EXPOSE 8000

CMD ["python", "app.py"]