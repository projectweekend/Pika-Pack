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
