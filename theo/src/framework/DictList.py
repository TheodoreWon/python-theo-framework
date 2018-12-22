import copy
import random
import collections
import os
import json
import csv


class DictList:
    """
    DictList is a simple data structure.
    DictList stores a list what is consist of dictionaries.

    If a key is set, quick sorting and binary searching is provided.
    The functionality gives us good performance for getting data.
    A variety of importing and exporting methods is supported. (JSON, CSV, MONGODB, etc.)
    And to refine a data, walker feature is supported.

    Attributes:
        key (str, optional): To support sorting and searching algorithm, a key is needed.
                                If the key is set, all of the datum dictionary should includes the key.

    Methods:
        dictlist = DictList(key=None)
        print(log=None)

        length = count() : getting the count value how many dictionaries are stored.
        datum = get_datum(value) : getting the dictionary datum what is matched with the stored key and argument value.
        datum = get_datum(filters) : getting the datum what is matched with argument filters.
        datum = get_datum(key, value) : getting the datum what is matched with argument key and argument value.
        data = get_data(filters=None) : getting the data what is matched with arguments filters.
        values = get_values(key, overlap=False, filters=None)
            filters (list): dictionary datum list. the filter has the key, 'key' and 'value'.

        append(datum) : appending argument datum
        insert(datum) : inserting argument datum at the first of the stored list
        extend(dictlist) : extending the data from argument dictlist
        extend_data(data) : extending the data

        remove_datum(datum) : removing argument datum if the datum is exist in the stored list
        datum = pop_datum(datum) : poping argument datum if the datum is exist in the stored list
        clear() : clear the stored list

        import_json(file) : importing the json data from json file
        export_json(file) : exporting the data what is stored list to csv file
        import_csv(file) : importing the json data from json file
        export_csv(file) : exporting the data what is stored list to csv file
            file (str): the file path (ex. os.path.join(os.getcwd(), 'files', 'data.json'))

        TODO: import_mongodb(database, collection)
        TODO: export_mongodb(database, collection)

        TODO: walker_handler = plug_in_walker(walker, walker_delay=False, insert=False)
        TODO: plug_out_walker(walker_handler)

    Example:
        contract_dictlist = DictList(key='name')
        contract_dictlist.import_csv(os.path.join(os.getcwd(), 'files', 'contract.csv'))
        contract_dictlist.print()

        contract_dictlist.append({'name': 'theo', 'email': 'taehee.won@gmail.com'})
        theo_contract = contract_dictlist.get_datum('theo')
        print(theo_contract) : {'name': 'theo', 'email': 'taehee.won@gmail.com'}
    """

    def __init__(self, key=None):
        if key is not None and not isinstance(key, str):
            raise AssertionError('key(type:{}) should be str.'.format(type(key)))

        self.data = list()

        self.key = key
        self.sorted = True

        self.walkers = list()

    def print(self, log=None):
        self.sort_data()

        if log is not None:
            from theo.src.framework.Log import Log
            if not isinstance(log, Log):
                raise AssertionError(
                    '[theo.framework.DictList] error: log(type:{}) should be theo.framework.Log.'.format(type(log)))

            log.print('info', 'DictList(num:{}/key:{}) walkers({})'.format(len(self.data), self.key, self.walkers))
            if len(self.data) <= 6:
                for index, datum in enumerate(self.data):
                    log.print('info', '{} {}'.format(index, datum))
            else:
                for index in [0, 1, 2]:
                    log.print('info', '{} {}'.format(index, self.data[index]))
                log.print('info', '...')
                for index in [-3, -2, -1]:
                    log.print('info', '{} {}'.format(len(self.data) + index, self.data[index]))

        else:
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
            self.validate_filters(attr1)

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
        self.validate_filters(filters)

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
        self.validate_filters(filters)

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
        self.validate_datum(self.key, datum)

        self.data.append(datum)
        self.sorted = False

    def insert(self, datum):
        self.validate_datum(self.key, datum)

        self.data.insert(0, datum)
        self.sorted = False

    def extend(self, dictlist):
        self.validate_dictlist(self.key, dictlist)

        if len(dictlist.count()):
            self.data.extend(dictlist.get_data())
            self.sorted = False

    def extend_data(self, data):
        self.validate_data(self.key, data)

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
        self.validate_file(file)

        if os.path.exists(file):
            file_handler = open(file, 'r')
            self.extend_data(json.load(file_handler))
            file_handler.close()

            self.sorted = False

    def export_json(self, file):
        self.validate_file(file)
        self.sort_data()

        if not os.path.exists(os.path.dirname(os.path.abspath(file))):
            os.makedirs(os.path.dirname(os.path.abspath(file)))

        file_handler = open(file, 'w')
        json.dump(self.data, file_handler, ensure_ascii=False, indent="\t")
        file_handler.close()

    def import_csv(self, file):
        self.validate_file(file)

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
        self.validate_file(file)
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
        try:
            from theo.src.framework.System import System
            from theo.database import MongoDB

            if 'MongoDBCtrl' in System.get_components():
                print('a')
                data = System.execute_interface('MongoDBCtrl', 'load_data', database, collection)
                if len(data):
                    self.data.extend(data)
                    self.sorted = False
            else:
                print('b')
                mongodb = MongoDB()
                data = mongodb.load_data(database, collection)
                if len(data):
                    self.data.extend(data)
                    self.sorted = False

                del mongodb

        except (ModuleNotFoundError, ImportError):
            raise AssertionError('[theo.framework.DictList] error: theo-database should be installed to use MongoDB.')

    def export_mongodb(self, database, collection):
        try:
            from theo.src.framework.System import System
            from theo.database import MongoDB

            self.sort_data()

            if 'MongoDBCtrl' in System.get_components():
                System.execute_interface('MongoDBCtrl', 'save_data', database, collection, self.data, self.key)
            else:
                mongodb = MongoDB()
                mongodb.save_data(database, collection, self.data, self.key)
                del mongodb

        except (ModuleNotFoundError, ImportError):
            raise AssertionError('[theo.framework.DictList] error: theo-database should be installed to use MongoDB.')

    """
    Internal sorting, searching functions

    When the getting functionality such as get_datum, get_data is called, the data is sorted.

    Methods:
        sort_data
        sort_data > is_data_ascending_order
        sort_data > is_data_descending_order
        sort_data > get_reversed_data
        sort_data > get_recursive_quick_sorted_data

        binary_search

    NOTE: Why here is the reverse?
            DictList could be used to store stock price data.
            Usually, the stock servers provide price data by reversed order.
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
                source_data = copy.copy(self.data)
                self.data.clear()
                self.data.extend(self.get_reversed_data(source_data))
                self.sorted = True
            else:
                source_data = copy.copy(self.data)
                self.data.clear()
                self.data.extend(self.get_recursive_quick_sorted_data(source_data, self.key))
                self.sorted = True

    @staticmethod
    def is_data_ascending_order(data, key):
        for index in range(1, len(data)):
            if data[index - 1][key] > data[index][key]:
                return False

        return True

    @staticmethod
    def is_data_descending_order(data, key):
        for index in range(1, len(data)):
            if data[index - 1][key] < data[index][key]:
                return False

        return True

    @staticmethod
    def get_reversed_data(data):
        reversed_data = list()
        for datum in reversed(data):
            reversed_data.append(datum)

        return reversed_data

    @staticmethod
    def get_recursive_quick_sorted_data(data, key):
        if len(data) > 1:
            pivot = data[random.randint(0, len(data) - 1)]
            left_data, middle_data, right_data = list(), list(), list()

            for index in range(len(data)):
                if data[index][key] < pivot[key]:
                    left_data.append(data[index])
                elif data[index][key] > pivot[key]:
                    right_data.append(data[index])
                else:
                    middle_data.append(data[index])

            return DictList.get_recursive_quick_sorted_data(left_data, key) \
                + middle_data \
                + DictList.get_recursive_quick_sorted_data(right_data, key)
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

    """
    Internal validation functions
    """
    @staticmethod
    def validate_datum(key, datum):
        if not isinstance(datum, dict):
            raise AssertionError('[theo.framework.DictList] error: datum(type:{}) should be dict.'.format(type(datum)))

        if key is not None and key not in datum:
            raise AssertionError(
                '[theo.framework.DictList] error: datum(keys:{}) does not have the key({}).'.format(
                    list(datum.keys()), key))

    @staticmethod
    def validate_data(key, data):
        if not isinstance(data, list):
            raise AssertionError('[theo.framework.DictList] error: data(type:{}) should be list.'.format(type(data)))

        if key is not None:
            for datum in data:
                if key not in datum:
                    raise AssertionError(
                        '[theo.framework.DictList] error: datum(keys:{}) does not have the key({}).'.format(
                            list(datum.keys()), key))

    @staticmethod
    def validate_dictlist(key, dictlist):
        if not isinstance(dict, DictList):
            raise AssertionError(
                '[theo.framework.DictList] error: dictlist(type:{}) should be DictList.'.format(type(dictlist)))

        DictList.validate_data(key, dictlist.get_data())

    @staticmethod
    def validate_filters(filters):
        if filters is not None:
            if not isinstance(filters, list):
                raise AssertionError(
                    '[theo.framework.DictList] error: filters(type:{}) should be list.'.format(type(filters)))

            for filter in filters:
                if not isinstance(filter, dict):
                    raise AssertionError(
                        '[theo.framework.DictList] error: filter(type:{}) should be dict.'.format(type(filter)))

                if not ('key' in filter and 'value' in filter):
                    raise AssertionError(
                        '[theo.framework.DictList] error: filter(keys:{}) does not have key or value.'.format(
                            list(filter.keys())))

    @staticmethod
    def validate_file(file):
        if not isinstance(file, str):
            raise AssertionError('[theo.framework.DictList] error: file(type:{}) should be str.'.format(type(file)))
