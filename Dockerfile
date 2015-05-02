FROM python:2.7.9
RUN mkdir src
WORKDIR /src
RUN pip install ipython pika pyecho
