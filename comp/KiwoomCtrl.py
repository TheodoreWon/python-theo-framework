import queue
import threading
import sys
sys.path.append('..')

from src.Component import Component
from src.System import system


def kiwoom_thread(log, kiwoom_queue, result_queue):
    from src.Kiwoom import Kiwoom
    kiwoom = Kiwoom()

    while True:
        messages = kiwoom_queue.get()

        if len(messages) == 1 and messages[0] == 'get_markets':
            result_queue.put(kiwoom.get_markets())

        elif len(messages) == 2 and messages[0] == 'get_codes':
            result_queue.put(kiwoom.get_codes(messages[1]))

        elif len(messages) == 3 and messages[0] == 'get_price_types':
            result_queue.put(kiwoom.get_price_types(messages[1], messages[2]))

        elif len(messages) == 3 and messages[0] == 'get_item':
            result_queue.put(kiwoom.get_item(messages[1], messages[2]))

        elif len(messages) == 4 and messages[0] == 'get_prices':
            result_queue.put(kiwoom.get_prices(messages[1], messages[2], messages[3]))

        elif len(messages) == 5 and messages[0] == 'get_prices':
            result_queue.put(kiwoom.get_prices(messages[1], messages[2], messages[3], messages[4]))

        else:
            raise AssertionError('messages({}) is not valid.'.format(messages))


class KiwoomCtrl(Component):
    execution_lock = None

    def set_related_components(self):
        self.related_components.clear()

    def initial(self):
        self.log.print('info', 'initial (related:{})'.format(self.related_components))

        system.register_interface(self.name, 'get_markets', [0], self.get_markets)
        system.register_interface(self.name, 'get_codes', [1], self.get_codes)
        system.register_interface(self.name, 'get_price_types', [2], self.get_price_types)
        system.register_interface(self.name, 'get_item', [2], self.get_item)
        system.register_interface(self.name, 'get_prices', [3, 4], self.get_prices)

        self.kiwoom_queue = queue.Queue()
        self.result_queue = queue.Queue()
        if self.execution_lock is None:
            self.execution_lock = threading.Lock()

        threading.Thread(target=kiwoom_thread, args=(self.log, self.kiwoom_queue, self.result_queue)).start()

    def get_markets(self):
        self.execution_lock.acquire()

        self.kiwoom_queue.put(['get_markets'])
        markets = self.result_queue.get()

        self.execution_lock.release()
        return markets

    def get_codes(self, market):
        self.execution_lock.acquire()

        self.kiwoom_queue.put(['get_codes', market])
        codes = self.result_queue.get()

        self.execution_lock.release()
        return codes

    def get_price_types(self, market, code):
        self.execution_lock.acquire()

        self.kiwoom_queue.put(['get_price_types', market, code])
        price_types = self.result_queue.get()

        self.execution_lock.release()
        return price_types

    def get_item(self, market, code):
        self.execution_lock.acquire()

        self.kiwoom_queue.put(['get_item', market, code])
        item = self.result_queue.get()

        self.execution_lock.release()
        return item

    def get_prices(self, market, code, price_type, range=None):
        self.execution_lock.acquire()

        self.kiwoom_queue.put(['get_prices', market, code, price_type, range])
        prices = self.result_queue.get()

        self.execution_lock.release()
        return prices
