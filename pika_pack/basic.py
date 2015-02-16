import json
import pika


class BasicProducer(object):

    def __init__(self, rabbit_url, exchange, exchange_type):
        self._rabbit_url = rabbit_url
        self._exchange = exchange
        self._exchange_type = exchange_type
        self._connection = pika.BlockingConnection(pika.URLParameters(self._rabbit_url))
        self._channel = self._connection.channel()
        self._channel.exchange_declare(exchange=self._exchange, type=self._exchange_type)

    def send(self, routing_key, message):
        self._channel.basic_publish(
            exchange=self._exchange,
            routing_key=routing_key,
            body=json.dumps(message))

    def stop(self):
        self._connection.close()
