FROM python:3.10-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENV PORT=8080

CMD [ "gunicorn", "--log-level=info", "gruhoedb.webserver:app" ]