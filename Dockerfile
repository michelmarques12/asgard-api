FROM docker.sieve.com.br/infra/alpine/py36/uwsgi20:0.0.2

#Version: 0.75.0-rc1
#Tag: sieve/infra/asgard-api

ARG _=""
ENV GIT_COMMIT_HASH=${_}

ENV UWSGI_MODULE=hollowman.app:application
ENV UWSGI_PROCESSES=4


WORKDIR /tmp
COPY Pipfile.lock /tmp/
COPY Pipfile /tmp/

RUN pip install -U pip pipenv \
&& apk -U add libpq \
&& apk add --virtual .deps postgresql-dev gcc g++ make python-dev \
&& pipenv install --system --deploy --ignore-pipfile \
&& apk del --purge .deps

COPY . /opt/app
WORKDIR /opt/app
