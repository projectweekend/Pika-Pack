import os
import sys
import pika_pack


RABBIT_IP = os.getenv('RABBIT_PORT_5672_TCP_ADDR')
assert RABBIT_IP
RABBIT_PORT = os.getenv('RABBIT_PORT_5672_TCP_PORT')
assert RABBIT_PORT
RABBIT_URL = 'amqp://{0}:{1}/'.format(RABBIT_IP, RABBIT_PORT)
EXCHANGE = 'testing_broadcaster'
QUEUE = 'testing_broadcaster'
ROUTING_KEY = 'testing_broadcaster'
MESSAGE = {
    'key': 'value'
}


def main():
    broadcaster = pika_pack.Broadcaster(RABBIT_URL, EXCHANGE)
    broadcaster.send(ROUTING_KEY, MESSAGE)
    broadcaster.stop()

    def action(message):
        assert message['key'] == 'value'
        print("Passed!")
        sys.exit(0)

    listener = pika_pack.Listener(
        RABBIT_URL,
        EXCHANGE,
        QUEUE,
        ROUTING_KEY,
        action)
    listener.run()


if __name__ == '__main__':
    main()
