import json
import pika


class BasicProducer(object):
    """This class connects to RabbitMQ, binds an 'exchange' then allows you to send \
    a message to a 'routing_key' using the 'send' method. It does not wait for any \
    response body message, just an acknowledgement it was received."""

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
