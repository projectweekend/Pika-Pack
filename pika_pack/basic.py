import json
import pika


class Producer(object):
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


class Sender(Producer):
    """This class sends messages to a 'direct' exchange, where only one consumer \
    will receive the message"""

    def __init__(self, rabbit_url, exchange):
        super(Sender, self).__init__(
            rabbit_url=rabbit_url,
            exchange=exchange,
            exchange_type='direct')


class Broadcaster(Producer):
    """This class sends messages to a 'fanout' exchange, where all consumers \
    will receive the message"""

    def __init__(self, rabbit_url, exchange):
        super(Broadcaster, self).__init__(
            rabbit_url=rabbit_url,
            exchange=exchange,
            exchange_type='fanout')
