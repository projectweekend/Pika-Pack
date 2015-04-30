import json
import pika


class Consumer(object):
    """This class connects to RabbitMQ, binds an 'exchange' then begins receiving \
    messages. It does not respond to the sender of the message, it only sends an \
    acknowledgement."""

    def __init__(self, rabbit_url, exchange, exchange_type, queue, routing_key, action):
        self._exchange = exchange
        self._exchange_type = exchange_type
        self._queue = queue
        self._routing_key = routing_key
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._url = rabbit_url
        self._action = action

    def _connect(self):
        return pika.SelectConnection(
            pika.URLParameters(self._url),
            self._on_connection_open,
            stop_ioloop_on_close=False)

    def _close_connection(self):
        self._connection.close()

    def _add_on_connection_close_callback(self):
        self._connection.add_on_close_callback(self._on_connection_closed)

    def _on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            self._connection.add_timeout(5, self._reconnect)

    def _on_connection_open(self, unused_connection):
        self._add_on_connection_close_callback()
        self._open_channel()

    def _reconnect(self):
        self._connection.ioloop.stop()

        if not self._closing:
            self._connection = self._connect()
            self._connection.ioloop.start()

    def _add_on_channel_close_callback(self):
        self._channel.add_on_close_callback(self._on_channel_closed)

    def _on_channel_closed(self, channel, reply_code, reply_text):
        self._connection.close()

    def _on_channel_open(self, channel):
        self._channel = channel
        self._add_on_channel_close_callback()
        self._setup_exchange(self._exchange)

    def _setup_exchange(self, exchange_name):
        self._channel.exchange_declare(
            self._on_exchange_declareok,
            exchange_name,
            self._exchange_type)

    def _on_exchange_declareok(self, unused_frame):
        self._setup_queue(self._queue)

    def _setup_queue(self, queue_name):
        self._channel.queue_declare(self._on_queue_declareok, queue_name)

    def _on_queue_declareok(self, method_frame):
        self._channel.queue_bind(
            self._on_bindok,
            self._queue,
            self._exchange,
            self._routing_key)

    def _add_on_cancel_callback(self):
        self._channel.add_on_cancel_callback(self._on_consumer_cancelled)

    def _on_consumer_cancelled(self, method_frame):
        if self._channel:
            self._channel.close()

    def _acknowledge_message(self, delivery_tag):
        self._channel.basic_ack(delivery_tag)

    def _on_message(self, ch, basic_deliver, props, body):
        self._action(json.loads(body))
        self._acknowledge_message(basic_deliver.delivery_tag)

    def _on_cancelok(self, unused_frame):
        self._close_channel()

    def _stop_consuming(self):
        if self._channel:
            self._channel.basic_cancel(self._on_cancelok, self._consumer_tag)

    def _start_consuming(self):
        self._add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self._on_message, self._queue)

    def _on_bindok(self, unused_frame):
        self._start_consuming()

    def _close_channel(self):
        self._channel.close()

    def _open_channel(self):
        self._connection.channel(on_open_callback=self._on_channel_open)

    def run(self):
        self._connection = self._connect()
        self._connection.ioloop.start()

    def stop(self):
        self._closing = True
        self._stop_consuming()
        self._connection.ioloop.start()


class Receiver(Consumer):
    """This class receives messages from a 'direct' exchange, where only one consumer \
    will receive the message."""

    def __init__(self, rabbit_url, exchange, queue, routing_key, action):
        super(Receiver, self).__init__(
            rabbit_url=rabbit_url,
            exchange=exchange,
            exchange_type='direct',
            queue=queue,
            routing_key=routing_key,
            action=action)


class Listener(Consumer):
    """This class receives messages from a 'fanout' exchange, where all consumers \
    will receive the message"""

    def __init__(self, rabbit_url, exchange, queue, routing_key, action):
        super(Listener, self).__init__(
            rabbit_url=rabbit_url,
            exchange=exchange,
            exchange_type='fanout',
            queue=queue,
            routing_key=routing_key,
            action=action)
