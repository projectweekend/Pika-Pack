This is a small collection of things that I've found useful working with [RabbitMQ](http://www.rabbitmq.com/) using the [Pika](https://pika.readthedocs.org/en/latest/) library.


### RPCBlockingConsumer

This class connects to RabbitMQ, binds an `exchange` and `routing_key`, and listens for new messages. The `request_action` parameter is a function that itself receives a single parameter of the incoming message body as a dictionary. This function is used to perform any custom operations, and should return another dictionary. The resulting dictionary becomes the message body that is sent back to the sender via the `reply_to` queue. The `reconnect_attempts` parameter is the number of times you would like the listener to attempt reconnection to RabbitMQ should the connection be lost after it starts to consume messages.

Once an instance of `RPCBlockingConsumer` is created, call the `start` method to begin processing messages. This is a blocking operation.

**Example:**
```python
RABBIT_URL = 'rabbit server connection URL'
EXCHANGE = 'name_of_exchange'
ROUTING_KEY = 'name_of_routing_key'
RECONNECT_ATTEMPTS = 3


def my_custom_action(message):
    # do something with message dictionary
    # return another dictionary as response
    return {'body': 'Message received!'}


rpc_consumer = RPCBlockingConsumer(
    rabbit_url=RABBIT_URL,
    exchange=EXCHANGE,
    routing_key=ROUTING_KEY,
    request_action=my_custom_action,
    reconnect_attempts=RECONNECT_ATTEMPTS)

rpc_consumer.start()
```


### RPCBlockingClient

This class connects to RabbitMQ, binds an 'exchange', then allows you to send a `message` to a `routing_key` using the `call` method. This method will block until it receives a response message from the RPC queue. The `call` method returns a dictionary representing the received message.

**Example:**
```python
RABBIT_URL = 'rabbit server connection URL'
EXCHANGE = 'name_of_exchange'


rpc_client = RPCBlockingClient(rabbit_url=RABBIT_URL, exchange=EXCHANGE)

message = {
    'body': 'Some message body'
}
# response will be a dictionary of the response message from RPCBlockingConsumer
response = rpc_client.call(routing_key='name_of_routing_key', message=message)
```

### Sender

This class sends messages to a 'direct' exchange, where only one consumer will receive the message.

**Example:**
```python
from pika_pack import Sender


RABBIT_URL = 'rabbit server connection URL'
EXCHANGE = 'name_of_exchange'


sender = Sender(rabbit_url=RABBIT_URL, exchange=EXCHANGE)

message = {
    'body': 'Some message body'
}

sender.send('some_routing_key', message)
```


### Broadcaster

This class sends messages to a 'fanout' exchange, where all consumers will receive the message.

**Example:**
```python
from pika_pack import Broadcaster


RABBIT_URL = 'rabbit server connection URL'
EXCHANGE = 'name_of_exchange'


broadcaster = Broadcaster(rabbit_url=RABBIT_URL, exchange=EXCHANGE)

message = {
    'body': 'Some message body'
}

broadcaster.send('some_routing_key', message)
```


### Receiver

This class receives messages from a 'direct' exchange, where only one consumer will receive the message.

**Example:**
```python
from pika_pack import Receiver
```


### Listener

This class receives messages from a 'fanout' exchange, where all consumers will receive the message.

**Example:**
```python
from pika_pack import Listener
```
