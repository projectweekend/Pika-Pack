import json
import pika
import pyecho

from exceptions import TooManyReconnectionAttempts


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


class Consumer(object):
    """This class connects to RabbitMQ, binds an 'exchange' then begins receiving \
    messages. It does not respond to the sender of the message, it only sends an \
    acknowledgement."""

    def __init__(self, rabbit_url, exchange, routing_key, request_action, reconnect_attempts=5):
        self._rabbit_url = rabbit_url
        self._exchange = exchange
        self._routing_key = routing_key
        self._request_action = request_action
        self._reconnect_attempts = reconnect_attempts
        self._connect()
        self._setup_channel()

    def _connect(self):
        self._connection = pika.BlockingConnection(pika.URLParameters(self._rabbit_url))

    def _reconnect(self):
        @pyecho.echo(self._reconnect_attempts)
        def attempt_reconnect():
            self._connect()
        try:
            attempt_reconnect()
        except pyecho.FailingTooHard:
            message = 'Reconnection attempts exceeded {0}'.format(self._reconnect_attempts)
            raise TooManyReconnectionAttempts(message)

    def _setup_channel(self):
        self._channel = self._connection.channel()

        result = self._channel.queue_declare(
            auto_delete=True,
            arguments={'x-message-ttl': 10000})

        self._channel.exchange_declare(exchange=self._exchange, type='direct')
        self._channel.queue_bind(
            queue=result.method.queue,
            exchange=self._exchange,
            routing_key=self._routing_key)
        self._channel.basic_qos(prefetch_count=1)
        self._channel.basic_consume(self._handle_request, queue=result.method.queue)

    def _handle_request(self, ch, method, props, body):
        # request action doesn't return anything
        self._request_action(json.loads(body))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        try:
            self._channel.start_consuming()
        except KeyboardInterrupt:
            self._channel.stop_consuming()
            self._connection.close()
        except pika.exceptions.AMQPConnectionError:
            self._reconnect()
            self._setup_channel()
            self.start()
