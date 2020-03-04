FROM python:3.7

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=citybike

WORKDIR /usr/local/app/

COPY Pipfile        /usr/local/app/
COPY Pipfile.lock   /usr/local/app/

RUN apt-get update && \
    apt-get install --no-install-recommends -y dumb-init python3 python3-pip gunicorn && \
    pip3 install --upgrade pip pipenv

COPY /deploy/run    /usr/local/app/
RUN groupadd -g 999 appgroup && \
    useradd -r -u 999 -d /usr/local/app -g appgroup appuser && \
    chown -R appuser:appgroup /usr/local/app && \
    chmod +x /usr/local/app/run
    
RUN su -c 'pipenv install' appuser

COPY /city_bike        /usr/local/app/city_bike

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/usr/local/app/run"]