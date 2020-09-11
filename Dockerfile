FROM python:3-alpine

# Install required packages for building app dependencies
RUN apk add --no-cache \
    gcc \
    linux-headers \
    musl-dev \
    pcre-dev \
    postgresql-dev && \
    pip3 install --no-cache-dir uwsgi

RUN addgroup -S app && adduser -S -G app app

ARG LOG_BASE_DIR
RUN mkdir -p ${LOG_BASE_DIR}

ARG APP_DIR
WORKDIR ${APP_DIR}

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

ENV CONFIG_DIR=${CONFIG_DIR}
COPY docker/scripts/* ./
COPY conf/espn-ffb-docker.ini ${CONFIG_DIR}/espn-ffb.ini

EXPOSE 5000

CMD uwsgi --ini ${CONFIG_DIR}/espn-ffb.ini
