FROM python:3.12.2

ENV PYTHONUNBUFFERED 1

COPY ./requirements.lock /
COPY ./requirements-dev.lock /
RUN sed '/-e/d' requirements.lock > requirements.txt
RUN sed '/-e/d' requirements-dev.lock > dev-requirements.txt

RUN pip install --upgrade pip && \
    pip install wheel && \
    pip install -r requirements.txt \
    pip install -r /dev-requirements.txt

WORKDIR /app
COPY . ./
RUN mkdir -p /var/log/api
EXPOSE $PORT/tcp
ENV PYTHONPATH app
