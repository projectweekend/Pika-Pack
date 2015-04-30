FROM python:2.7.9
ADD pika_pack /src/pika_pack
WORKDIR /src
RUN pip install ipython pika pyecho
