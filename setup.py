from distutils.core import setup

setup(
    name='Pika-Pack',
    version='1.0.2',
    author='Brian Hines',
    author_email='brian@projectweekend.net',
    packages=['pika_pack'],
    url='https://github.com/projectweekend/Pika-Pack',
    license='LICENSE.txt',
    description='Handy components when working with RabbitMQ and Pika (https://pika.readthedocs.org/en/latest/).',
    long_description=open('README.txt').read(),
    install_requires=[
        "pika == 0.9.14",
        "pyecho == 0.0.2",
    ],
)
