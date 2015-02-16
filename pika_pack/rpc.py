import json
import pika
import pyecho

from exceptions import TooManyReconnectionAttempts


class RPCBlockingListener(object):
    """This class connects to RabbitMQ, binds an 'exchange' and 'routing_key', and listens for \
    new messages. The 'request_action' parameter is a function that receives a single parameter \
    of the incoming message body as a dictionary. This function is used to perform any custom \
    operations, and returns another dictionary. The resulting dictionary becomes the message body \
    that is sent back to the sender via the `reply_to` queue. The 'reconnect_attempts' parameter \
    is the number of times you would like the listener to attempt reconnection to RabbitMQ should \
    the connection be lost after it starts to consume messages.

    Once an instance of RPCBlockingListener is created, call the `start` method to begin \
    processing messages. This is a blocking operation.
    """

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
        response = self._request_action(json.loads(body))
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=json.dumps(response))
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