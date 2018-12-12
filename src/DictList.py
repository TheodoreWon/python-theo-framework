import copy
import random
import collections
import os
import json
import csv

from .Validation import Validation


class DictList:
    """
    DictList is a simple data structure.
    DictList stores a list what is consist of dictionaries.

    If a key is set, quick sorting and binary searching is provided.
    The functionality gives us good performance for getting data.
    A variety importing and exporting methods is supported. JSON, CSV, MONGODB
    And to refine a data, walker feature is supported.

    Methods:
        dictlist = DictList(key=None)
        print()

        length = count()
        datum = get_datum(value)
        datum = get_datum(filters)
        datum = get_datum(key, value)
        data = get_data(filters=None)
        values = get_values(key, overlap=False, filters=None)

        append(datum)
        insert(datum)
        extend(dictlist)
        extend_data(data)

        remove_datum(datum)
        datum = pop_datum(datum)
        clear()

        import_json(file)
        export_json(file)
        import_csv(file)
        export_csv(file)
        import_mongodb(database, collection)
        export_mongodb(database, collection)

        TODO: walker_handler = plug_in_walker(walker, walker_delay=False, insert=False)
        TODO: plug_out_walker(walker_handler)

    Development guide:
        External function should validate parameters before calling an internal function.
    """

    def __init__(self, key=None):
        if key is not None and not isinstance(key, str):
            raise AssertionError('key(type:{}) should be str.'.format(type(key)))

        self.data = list()

        self.key = key
        self.sorted = True

        self.walkers = list()

    def print(self):
        self.sort_data()

        print('DictList(num:{}/key:{}) walkers({})'.format(len(self.data), self.key, self.walkers))
        if len(self.data) <= 6:
            for index, datum in enumerate(self.data):
                print('{} {}'.format(index, datum))
        else:
            for index in [0, 1, 2]:
                print('{} {}'.format(index, self.data[index]))
            print('...')
            for index in [-3, -2, -1]:
                print('{} {}'.format(len(self.data) + index, self.data[index]))

    def count(self):
        return len(self.data)

    def get_datum(self, attr1, attr2=None):
        # get_datum(filters)
        if attr2 is None and isinstance(attr1, list):
            Validation.validate_filters(attr1)

            filters = attr1
            for datum in self.data:
                for filter in filters:
                    if not (filter['key'] in datum and datum[filter['key']] == filter['value']):
                        break
                else:
                    return copy.copy(datum)

            return None

        # get_datum(value)
        elif attr2 is None:
            if self.key is None:
                raise AssertionError('get_datum(value) needs key in DictList.')

            value = attr1
            return copy.copy(self.binary_search_datum(value))

        # get_datum(key, value)
        else:
            if not isinstance(attr1, str):
                raise AssertionError('key(type:{}) should be str.'.format(type(attr1)))

            key = attr1
            value = attr2

            if self.key is not None and self.key == key:
                return copy.copy(self.binary_search_datum(value))
            else:
                for datum in self.data:
                    if key in datum and datum[key] == value:
                        return copy.copy(datum)

                return None

    def get_data(self, filters=None):
        Validation.validate_filters(filters)

        if filters is None:
            return copy.copy(self.data)

        else:
            data = list()
            for datum in self.data:
                for filter in filters:
                    if not (filter['key'] in datum and datum[filter['key']] == filter['value']):
                        break
                else:
                    data.append(datum)

            return data

    def get_values(self, key, overlap=False, filters=None):
        Validation.validate_filters(filters)

        if filters is None:
            filters = list()

        values = list()
        for datum in self.data:
            if key not in datum:
                continue

            for filter in filters:
                if not (filter['key'] in datum and datum[filter['key']] == filter['value']):
                    break
            else:
                values.append(datum[key])

        if overlap:
            return values
        else:
            return list(collections.OrderedDict.fromkeys(values))

    def append(self, datum):
        Validation.validate_datum(self.key, datum)

        self.data.append(datum)
        self.sorted = False

    def insert(self, datum):
        Validation.validate_datum(self.key, datum)

        self.data.insert(0, datum)
        self.sorted = False

    def extend(self, dictlist):
        Validation.validate_dictlist(self.key, dictlist)

        if len(dictlist.count()):
            self.data.extend(dictlist.get_data())
            self.sorted = False

    def extend_data(self, data):
        Validation.validate_data(self.key, data)

        if len(data):
            self.data.extend(data)
            self.sorted = False

    def pop_datum(self, datum):
        if datum in self.data:
            self.data.remove(datum)
            return datum

        return None

    def remove_datum(self, datum):
        if datum in self.data:
            self.data.remove(datum)

    def clear(self):
        self.data.clear()
        self.sorted = True

    def import_json(self, file):
        Validation.validate_file(file)

        if os.path.exists(file):
            file_handler = open(file, 'r')
            self.extend_data(json.load(file_handler))
            file_handler.close()

            self.sorted = False

    def export_json(self, file):
        Validation.validate_file(file)
        self.sort_data()

        if not os.path.exists(os.path.dirname(os.path.abspath(file))):
            os.makedirs(os.path.dirname(os.path.abspath(file)))

        file_handler = open(file, 'w')
        json.dump(self.data, file_handler, ensure_ascii=False, indent="\t")
        file_handler.close()

    def import_csv(self, file):
        Validation.validate_file(file)

        if os.path.exists(file):
            file_handler = open(file, 'r', encoding='utf-8-sig')
            csv_reader = csv.reader(file_handler)
            keys = list()
            for index, values in enumerate(csv_reader):
                if index == 0:
                    for value in values:
                        keys.append(value)
                else:
                    datum = dict()
                    for key_index, key in enumerate(keys):
                        datum[key] = values[key_index]

                    self.append(datum)

            file_handler.close()

            self.sorted = False

    def export_csv(self, file):
        Validation.validate_file(file)
        self.sort_data()

        if not os.path.exists(os.path.dirname(os.path.abspath(file))):
            os.makedirs(os.path.dirname(os.path.abspath(file)))

        if len(self.data) != 0:
            file_handler = open(file, 'w', encoding='utf-8-sig', newline='\n')
            keys = list(self.data[0].keys())
            csv_writer = csv.writer(file_handler)
            csv_writer.writerow(keys)
            for datum in self.data:
                values = list()
                for key in keys:
                    values.append(str(datum.get(key)))

                csv_writer.writerow(values)

            file_handler.close()

    def import_mongodb(self, database, collection):
        Validation.validate_mongodb(database, collection)

        from .System import system
        data = system.execute_interface('MongoDBCtrl', 'load_data', database, collection)
        if len(data):
            self.data.extend(data)
            self.sorted = False

    def export_mongodb(self, database, collection):
        Validation.validate_mongodb(database, collection)
        self.sort_data()

        from .System import system
        system.execute_interface('MongoDBCtrl', 'save_data', database, collection, self.data, self.key)

    """
    Internal sorting, searching functions

    When the getting functionality such as get_datum, get_data is called, the data is sorted.

    Methods:
        sort_data
        sort_data > is_data_ascending_order
        sort_data > is_data_descending_order
        sort_data > reverse_data_order
        sort_data > recursive_quick_sort

        binary_search

    NOTE: Why the reverse function is worked?
            Theo usually use the DictList to store stock price data.
            From stock server, the price data is reversed.
            To sort reversed data, the sorting algorithm works as the worst performance.
            That is why the reverse function is exist.

    NOTE: The sorting method is the recursive quick sorting.
            If sorting works over limitation time recursively, exception happens.
            RecursionError: maximum recursion depth exceeded in comparison
            Iterative quick sorting could be needed.
            But, the recursive quick sorting's performance is better than the other.
    """
    def sort_data(self):
        if self.key is not None and not self.sorted:
            if self.is_data_ascending_order(self.data, self.key):
                self.sorted = True
            elif len(self.walkers):
                raise AssertionError('The data cannot be sorted. Walkers are working.')
            elif self.is_data_descending_order(self.data, self.key):
                self.reverse_data_order(self.data)
                self.sorted = True
            else:
                self.recursive_quick_sort_data(self.data, self.key)
                self.sorted = True

    @staticmethod
    def is_data_ascending_order(data, key):
        if len(data) < 2:
            return True

        for index in range(1, len(data)):
            if data[index - 1][key] > data[index][key]:
                return False

        return True

    @staticmethod
    def is_data_descending_order(data, key):
        if len(data) < 2:
            return True

        for index in range(2, len(data)):
            if data[index - 1][key] < data[index][key]:
                return False

        return True

    @staticmethod
    def reverse_data_order(data):
        source_data = copy.copy(data)
        data.clear()
        for datum in reversed(source_data):
            data.append(datum)

    @staticmethod
    def recursive_quick_sort_data(data, key):
        if len(data) > 1:
            pivot = data[random.randint(0, len(data) - 1)]
            left_list, middle_list, right_list = list(), list(), list()

            for index in range(len(data)):
                if data[index][key] < pivot[key]:
                    left_list.append(data[index])
                elif data[index][key] > pivot[key]:
                    right_list.append(data[index])
                else:
                    middle_list.append(data[index])

            return DictList.recursive_quick_sort_data(left_list, key) \
                + middle_list \
                + DictList.recursive_quick_sort_data(right_list, key)
        else:
            return data

    def binary_search_datum(self, value):
        self.sort_data()

        start_index = 0
        last_index = self.count() - 1

        while start_index <= last_index:
            index = (start_index + last_index) // 2

            if self.data[index][self.key] > value:
                last_index = index - 1
            elif self.data[index][self.key] < value:
                start_index = index + 1
            else:
                return self.data[index]

        return None
