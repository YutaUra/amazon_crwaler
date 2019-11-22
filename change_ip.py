from stem import Signal
from stem.control import Controller
import logging


def change_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='thym3594')
        controller.signal(Signal.NEWNYM)
    logging.debug('changed ip')


if __name__ == '__main__':
    change_ip()
