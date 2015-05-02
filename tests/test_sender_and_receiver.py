import os
import sys
import pika_pack


RABBIT_IP = os.getenv('RABBIT_PORT_5672_TCP_ADDR')
assert RABBIT_IP
RABBIT_PORT = os.getenv('RABBIT_PORT_5672_TCP_PORT')
assert RABBIT_PORT
RABBIT_URL = 'amqp://{0}:{1}/'.format(RABBIT_IP, RABBIT_PORT)
EXCHANGE = 'testing'
QUEUE = 'testing'
ROUTING_KEY = 'testing'
MESSAGE = {
    'key': 'value'
}


def main():
    sender = pika_pack.Sender(RABBIT_URL, EXCHANGE)
    sender.send(ROUTING_KEY, MESSAGE)
    sender.stop()

    def action(message):
        assert message['key'] == 'value'
        print("Passed!")
        sys.exit(0)

    receiver = pika_pack.Receiver(
        RABBIT_URL,
        EXCHANGE,
        QUEUE,
        ROUTING_KEY,
        action)
    receiver.run()


if __name__ == '__main__':
    main()
