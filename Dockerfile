#FROM python:3.9-slim-bullseye
#
## установка часового пояся Europe/Moscow
#
#RUN /bin/cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime && echo 'Europe/Moscow' >/etc/timezone
#
#RUN pip install --upgrade pip
#RUN adduser --disabled-password myuser
#USER myuser
#
#WORKDIR /var/www/html
#
##COPY requirements.txt requirements.txt
#COPY --chown=myuser:myuser requirements.txt requirements.txt
#RUN pip install --user -r requirements.txt

#RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.9-alpine

# установка часового пояся Europe/Moscow
RUN /bin/cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime && echo 'Europe/Moscow' >/etc/timezone

RUN pip install --upgrade pip

RUN adduser -D myuser
USER myuser
WORKDIR /home/myuser

COPY --chown=myuser:myuser requirements.txt requirements.txt
RUN pip install --user -r requirements.txt

ENV PATH="/home/myuser/.local/bin:${PATH}"

COPY --chown=myuser:myuser . .

CMD ["python", "bot_main.py"]