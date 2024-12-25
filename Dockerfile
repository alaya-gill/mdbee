
FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

RUN apk update \
  # psycopg2 dependencies
  && apk add --virtual build-deps gcc python3-dev musl-dev \
  && apk add postgresql-dev \
  # Pillow dependencies
  && apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
  # CFFI dependencies
  && apk add libffi-dev py-cffi g++
  # weasyprint dependencies

RUN apk --update --upgrade add libffi-dev cairo-dev pango-dev gdk-pixbuf-dev openssl-dev cargo fontconfig font-noto

RUN apk --update --upgrade add --no-cache chromium 

RUN addgroup -S django \
    && adduser -S -G django django

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/production.txt \
    && rm -rf /requirements

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint
RUN chown django /entrypoint

COPY ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
RUN chown django /start

COPY ./compose/production/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker
RUN chown django /start-celeryworker

COPY ./compose/production/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat
RUN chown django /start-celerybeat

COPY ./compose/production/django/start-channelworker /start-channelworker
RUN sed -i 's/\r$//g' /start-channelworker
RUN chmod +x /start-channelworker
RUN chown django /start-channelworker

COPY . /app

RUN chown -R django /app

USER django

WORKDIR /app

ENV REDIS_URL redis://synergy-cloud-redis-replica.a5qkxi.ng.0001.use2.cache.amazonaws.com:6379:6379/0

EXPOSE 8000

