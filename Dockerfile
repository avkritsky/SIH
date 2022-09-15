FROM python:3.9-slim-bullseye

# установка часового пояся Europe/Moscow

RUN /bin/cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime && echo 'Europe/Moscow' >/etc/timezone

WORKDIR /var/www/html

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt