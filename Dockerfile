FROM python:3.10.8-slim

RUN apt-get update && apt-get install -y postgresql-dev

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY ./Evaluator/ /usr/src/app

RUN pip install --no-cache-dir -r requirements.txt
COPY ./utils/ /usr/src/utils

EXPOSE 80

CMD ["sh", "/usr/src/utils/run.sh"]
