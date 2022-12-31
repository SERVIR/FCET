FROM python:3.10.8-slim

RUN apt-get update && apt-get -y install libpq-dev gcc

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY ./Evaluator/ /usr/src/app

RUN pip install -U pip && pip install --no-cache-dir -r requirements.txt
COPY ./utils/ /usr/src/utils

EXPOSE 80

CMD ["sh", "/usr/src/utils/run.sh"]
