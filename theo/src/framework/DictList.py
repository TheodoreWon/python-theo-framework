import os
import json
import csv


class DictList:
    """
    DictList is a simple list structure.
    DictList stores a list what is consist of dictionaries.
    A variety of importing and exporting methods is supported. (JSON, CSV, MONGODB, etc.)
    And to refine a list, walker feature is supported.

    Attributes:
        key (str, optional): To support sorting and searching algorithm, a key is needed.
                                If the key is set, all of the element dictionary should includes the key.

    Methods:
        dictlist = DictList(key=None)

        str(dictlist)
        dictlist.print(print_all=False)
        length = dictlist.count() : getting the count value how many dictionaries are stored

        element = dictlist.get(value)      : getting the element what is matched with the stored key and argument value
        element = dictlist.get(key, value) : getting the element what is matched with argument key and argument value
        element = dictlist.get(queries)    : getting the element what is matched with argument queries
            queries (list): the list of queries
            query (dictionary) : the key 'key', 'value' should be included to find

        list = dictlist.get_list()           : getting the list what is stored
        list = dictlist.get_list(value)      : getting the list what is matched with the stored key and argument value
        list = dictlist.get_list(key, value) : getting the list what is matched with argument key and argument value
        list = dictlist.get_list(queries)    : getting the list what is matched with argument queries

        list = values(key, overlap=False, sort=False)

        dictlist.append(element)   : appending argument element
        dictlist.insert(element)   : inserting argument element at the first of the stored list
        dictlist.extend(dictlist)  : extending the list from argument dictlist
        dictlist.extend_list(list) : extending the list

        dictlist.remove(element) : removing argument element if the element is exist in the stored list
        element = dictlist.pop(element) : poping argument element if the element is exist in the stored list
        dictlist.clear() : clear the stored list

        dictlist.import_json(file, encoding='UTF-8-sig') : importing the json data from json file
        dictlist.export_json(file, encoding='UTF-8-sig') : exporting the data what is stored list to csv file
        dictlist.import_csv(file, encoding='UTF-8-sig', separator=',') : importing the json data from json file
        dictlist.export_csv(file, encoding='UTF-8-sig') : exporting the data what is stored list to csv file
            file (str): the file path (ex. os.path.join(os.getcwd(), 'files', 'data.json'))

        dictlist.import_mongodb(database, collection, range_filter=None) : importing the data from mongodb
        dictlist.export_mongodb(database, collection) : exporting the datawhat is stored list to mongodb

        walker_handler = dictlist.plug_in_walker(walker, walker_delay=False, insert=False)
        dictlist.plug_out_walker(walker_handler)

    Example:
        contract_dictlist = DictList(key='name')
        contract_dictlist.import_csv(os.path.join(os.getcwd(), 'files', 'contract.csv'))
        contract_dictlist.print()

        contract_dictlist.append({'name': 'theo', 'email': 'taehee.won@gmail.com'})
        theo_contract = contract_dictlist.get('theo')
        print(theo_contract) : {'name': 'theo', 'email': 'taehee.won@gmail.com'}
    """

    def __init__(self, key=None):
        self.data = list()

        self.key = key if key is not None and isinstance(key, str) else None
        self.sorted = True

        self.walkers = list()

    def __str__(self):
        return f'DictList(num:{len(self.data)}/key:{self.key}' \
               + (f')' if not len(self.walkers) else f'/walkers:{len(self.walkers)})')

    def print(self, print_all=None):
        try:
            if self.key is not None and not self.sorted:
                self.data.sort(key=lambda element: element[self.key])
                self.sorted = True
        except Exception as error:
            print(f'error: {error} / dictlist.print(print_all:{print_all}/{type(print_all)})')
            print(f'\tno value for the key({self.key}) at',
                  f'{list(filter(lambda element: self.key not in element, self.data))}')
            return

        try:
            print(str(self))
            if print_all or len(self.data) <= 6:
                for index, element in enumerate(self.data):
                    print(f'[index:{index}] {element}')
            else:
                for index in [0, 1, 2]:
                    print(f'[index:{index}] {self.data[index]}')
                print('...')
                for index in [-3, -2, -1]:
                    print(f'[index:{len(self.data) + index}] {self.data[index]}')
        except Exception as error:
            print(f'error: {error} / dictlist.print(print_all:{print_all}/{type(print_all)})')

    def count(self):
        return len(self.data)

    def get(self, attr1, attr2=None):
        try:
            if self.key and not self.sorted:
                self.data.sort(key=lambda element: element[self.key])
                self.sorted = True
        except Exception as error:
            print(f'error: {error} / dictlist.get(attr1:{attr1}/{type(attr1)}, attr2:{attr2}/{type(attr2)})')
            print(f'\tno value for the key({self.key}) at',
                  f'{list(filter(lambda element: self.key not in element, self.data))}')
            return None

        # element = get(queries) : getting the element what is matched with argument queries
        if not attr2 and isinstance(attr1, list):
            try:
                if not len(attr1):
                    raise

                for element in self.data:
                    for query in attr1:
                        if not (query['key'] in element and element[query['key']] == query['value']):
                            break
                    else:
                        return element

                return None
            except Exception as error:
                print(f'error: {error} / dictlist.get(queries:{attr1}/{type(attr1)})')
                print('\telement = dictlist.get(queries) : getting the element what is matched with argument queries')
                return None

        # element = dictlist.get(value) : getting the element what is matched with the stored key and argument value
        elif not attr2:
            try:
                left_index, right_index = 0, len(self.data) - 1
                while left_index <= right_index:
                    index = (left_index + right_index) // 2

                    if self.data[index][self.key] > attr1:
                        right_index = index - 1
                    elif self.data[index][self.key] < attr1:
                        left_index = index + 1
                    else:
                        return self.data[index]

                return None
            except Exception as error:
                print(f'error: {error} / dictlist.get(value:{attr1}/{type(attr1)})')
                print('\telement = dictlist.get(value) : getting the element what is matched with the stored key and argument value')
                if len(self.walkers):
                    print('\tif you set the key, the key could be cleared by activation of walker')
                return None

        # element = dictlist.get(key, value) : getting the element what is matched with argument key and argument value
        else:
            try:
                for element in self.data:
                    if attr1 in element and element[attr1] == attr2:
                        return element

                return None
            except Exception as error:
                print(f'error: {error} / dictlist.get(key:{attr1}/{type(attr1)}, value:{attr2}/{type(attr2)})')
                print('\telement = dictlist.get(key, value) : getting the element what is matched with argument key and argument value')
                return None

    def get_list(self, attr1=None, attr2=None):
        try:
            if self.key and not self.sorted:
                self.data.sort(key=lambda element: element[self.key])
                self.sorted = True
        except Exception as error:
            print(f'error: {error} / dictlist.get_list(attr1:{attr1}/{type(attr1)}, attr2:{attr2}/{type(attr2)})')
            print(f'\tno value for the key({self.key}) at',
                  f'{list(filter(lambda element: self.key not in element, self.data))}')
            return None

        # list = dictlist.get_list() : getting the list what is stored
        if attr1 is None and attr2 is None:
            return self.data

        # list = dictlist.get_list(queries) : getting the list what is matched with argument queries
        if not attr2 and isinstance(attr1, list):
            try:
                if not len(attr1):
                    raise

                data = list()
                for element in self.data:
                    for query in attr1:
                        if not (query['key'] in element and element[query['key']] == query['value']):
                            break
                    else:
                        data.append(element)

                return data
            except Exception as error:
                print(f'error: {error} / dictlist.get_list(queries:{attr1}/{type(attr1)})')
                print('\tlist = dictlist.get_list(queries) : getting the list what is matched with argument queries')
                return None

        # list = dictlist.get_list(value) : getting the list what is matched with the stored key and argument value
        elif not attr2:
            try:
                return list(filter(lambda element: element[self.key] == attr1, self.data))
            except Exception as error:
                print(f'error: {error} / dictlist.get_list(value:{attr1}/{type(attr1)})')
                print('\tlist = dictlist.get_list(value) :',
                      'getting the list what is matched with the stored key and argument value')
                return None

        # list = dictlist.get_list(key, value) : getting the list what is matched with argument key and argument value
        else:
            try:
                return list(filter(lambda element: element[attr1] == attr2, self.data))
            except Exception as error:
                print(f'error: {error} / dictlist.get_list(key:{attr1}/{type(attr1)}, value:{attr2}/{type(attr2)})')
                print('\tlist = dictlist.get_list(key, value) :',
                      'getting the list what is matched with argument key and argument value')
                return None

    def values(self, key, overlap=False, sort=False):
        try:
            if self.key and not self.sorted:
                self.data.sort(key=lambda element: element[self.key])
                self.sorted = True
        except Exception as error:
            print(f'error: {error} / dictlist.values(key:{key}/{type(key)})')
            print(f'\tno value for the key({self.key}) at',
                  f'{list(filter(lambda element: self.key not in element, self.data))}')
            return None

        try:
            values = list(map(lambda element: element[key], filter(lambda element: key in element, self.data)))
            if not overlap: values = list(set(values))
            if sort:        values.sort()
            return values
        except Exception as error:
            print(f'error: {error} / dictlist.values(key:{key}/{type(key)},',
                  f'overlap:{overlap}/{type(overlap)}, sort:{sort}/{type(sort)})')
            return None

    def append(self, element):
        try:
            self.data.append(element)
            self.sorted = False

            self.run_walker()
        except Exception as error:
            print(f'error: {error} / dictlist.append(element:{element}/{type(element)})')

    def insert(self, element):
        try:
            self.data.insert(0, element)
            self.sorted = False

            self.run_walker()
        except Exception as error:
            print(f'error: {error} / dictlist.insert(element:{element}/{type(element)})')

    def extend(self, dictlist):
        try:
            if dictlist.count():
                self.data.extend(dictlist.get_list())
                self.sorted = False

                self.run_walker()
        except Exception as error:
            print(f'error: {error} / dictlist.extend(dictlist:{dictlist}/{type(dictlist)})')

    def extend_list(self, data):
        try:
            if len(data):
                self.data.extend(data)
                self.sorted = False

                self.run_walker()
        except Exception as error:
            print(f'error: {error} / dictlist.extend_list(list:{data}/{type(data)})')

    def remove(self, element):
        try:
            self.data.remove(element)
        except Exception as error:
            print(f'error: {error} / dictlist.remove(element:{element}/{type(element)})')

    def pop(self, element):
        try:
            if element in self.data:
                self.data.remove(element)
                return element

            return None
        except Exception as error:
            print(f'error: {error} / dictlist.remove(element:{element}/{type(element)})')
            return None

    def clear(self):
        self.data.clear()
        self.sorted = True

    def import_json(self, file, encoding='UTF-8-sig'):
        try:
            if os.path.exists(file):
                file_handler = open(file, 'r', encoding=encoding)
                data = json.load(file_handler)
                file_handler.close()

                if len(data):
                    self.data.extend(data)
                    self.sorted = False

                    self.run_walker()
        except Exception as error:
            print(f'error: {error} / dictlist.import_json(file:{file}/{type(file)},',
                  f'encoding:{encoding}/{type(encoding)})')

    def export_json(self, file, encoding='UTF-8-sig'):
        try:
            if self.key and not self.sorted:
                self.data.sort(key=lambda element: element[self.key])
                self.sorted = True
        except Exception as error:
            print(f'error: {error} / dictlist.import_json(file:{file}/{type(file)}, encoding:{encoding}/{type(encoding)})')
            print(f'\tno value for the key({self.key}) at',
                  f'{list(filter(lambda element: self.key not in element, self.data))}')
            return None

        try:
            if len(self.data):
                if not os.path.exists(os.path.dirname(os.path.abspath(file))):
                    os.makedirs(os.path.dirname(os.path.abspath(file)))

                file_handler = open(file, 'w', encoding=encoding)
                json.dump(self.data, file_handler, ensure_ascii=False, indent="\t")
                file_handler.close()
        except Exception as error:
            print(f'error: {error} / dictlist.import_json(file:{file}/{type(file)},',
                  'encoding:{encoding}/{type(encoding)})')

    def import_csv(self, file, encoding='UTF-8-sig', separator=','):
        try:
            if os.path.exists(file):
                file_handler = open(file, 'r', encoding=encoding)
                csv_reader = csv.reader(file_handler, delimiter=separator)
                data = list()
                for index, values in enumerate(csv_reader):
                    if index == 0:
                        keys = list(map(lambda value: value, values))
                    else:
                        element = dict()
                        for key_index, key in enumerate(keys):
                            if values[key_index]:
                                element[key] = values[key_index]

                        data.append(element)

                file_handler.close()

                if len(data):
                    self.data.extend(data)
                    self.sorted = False

                    self.run_walker()
        except Exception as error:
            print(f'error: {error} / dictlist.import_csv(file:{file}/{type(file)},',
                  f'encoding:{encoding}/{type(encoding)})')

    def export_csv(self, file, encoding='UTF-8-sig'):
        try:
            if self.key and not self.sorted:
                self.data.sort(key=lambda element: element[self.key])
                self.sorted = True
        except Exception as error:
            print(f'error: {error} / dictlist.export_csv(file:{file}/{type(file)}, encoding:{encoding}/{type(encoding)})')
            print(f'\tno value for the key({self.key}) at'
                  f'{list(filter(lambda element: self.key not in element, self.data))}')
            return None

        try:
            if len(self.data):
                if not os.path.exists(os.path.dirname(os.path.abspath(file))):
                    os.makedirs(os.path.dirname(os.path.abspath(file)))

                file_handler = open(file, 'w', encoding=encoding, newline='\n')
                keys = list(self.data[0].keys())
                csv_writer = csv.writer(file_handler)
                csv_writer.writerow(keys)
                for element in self.data:
                    csv_writer.writerow(list(map(lambda key: str(element.get(key)) if key in element else '', keys)))

                file_handler.close()
        except Exception as error:
            print(f'error: {error} / dictlist.export_csv(file:{file}/{type(file)},',
                  f'encoding:{encoding}/{type(encoding)})')

    def import_mongodb(self, database, collection, range_filter=None):
        try:
            from theo.src.framework.System import System
            from theo.database import MongoDB

            if 'MongoDBCtrl' in System.get_components():
                data = System.execute_interface(
                    'MongoDBCtrl', 'select', database, collection, self.key, None, range_filter)
            else:
                mongodb = MongoDB()
                data = mongodb.select(database, collection, sorting_key=self.key, range=range_filter)
                del mongodb

            if len(data):
                self.data.extend(data)
                self.sorted = False
                self.run_walker()
        except Exception as error:
            print(f'error: {error} / dictlist.import_mongodb(database:{database}/{type(database)},',
                  f'collection:{collection}/{type(collection)}, range:{range}/{type(range)})')

    def export_mongodb(self, database, collection):
        try:
            if self.key and not self.sorted:
                self.data.sort(key=lambda element: element[self.key])
                self.sorted = True
        except Exception as error:
            print(f'error: {error} / dictlist.export_mongodb(database:{database}/{type(database)},',
                  f'collection:{collection}/{type(collection)})')
            print(f'tno value for the key({self.key}) at',
                  f'{list(filter(lambda element: self.key not in element, self.data))}')
            return None

        try:
            if len(self.data):
                from theo.src.framework.System import System
                from theo.database import MongoDB

                if 'MongoDBCtrl' in System.get_components():
                    System.execute_interface('MongoDBCtrl', 'insert', database, collection, self.data, self.key)
                else:
                    mongodb = MongoDB()
                    mongodb.insert(database, collection, self.data, unique_key=self.key)
                    del mongodb
        except Exception as error:
            print(f'error: {error} / dictlist.export_mongodb(database:{database}/{type(database)},',
                  f'collection:{collection}/{type(collection)})')

    def plug_in_walker(self, walker, walker_delay=False, insert=False):
        try:
            if self.key and not self.sorted:
                self.data.sort(key=lambda element: element[self.key])
                self.sorted = True
        except Exception as error:
            print(f'error: {error} / dictlist.plug_in_walker(walker:{walker}/{type(walker)},',
                  f'walker_delay:{walker_delay}/{type(walker_delay)}, insert:{insert}/{type(insert)})')
            print(f'\tno value for the key({self.key}) at',
                  f'{list(filter(lambda element: self.key not in element, self.data))}')
            return None

        try:
            handler = {'index': 0, 'walker': walker}
            if insert:
                self.walkers.insert(0, handler)
            else:
                self.walkers.append(handler)

            if not walker_delay:
                self.run_walker()

            self.key = None

            return handler
        except Exception as error:
            print(f'error: {error} / dictlist.plug_in_walker(walker:{walker}/{type(walker)},',
                  f'walker_delay:{walker_delay}/{type(walker_delay)}, insert:{insert}/{type(insert)})')
            return None

    def plug_out_walker(self, handler):
        try:
            self.walkers.remove(handler)
        except Exception as error:
            print(f'error: {error} / dictlist.plug_out_walker(handler:{handler}/{type(handler)})')

    def run_walker(self):
        try:
            if len(self.walkers):
                index = min(map(lambda walker: walker['index'], self.walkers))
                while index != len(self.data):
                    for walker in self.walkers:
                        if walker['index'] == index:
                            walker['walker'](self.data[index])
                            walker['index'] = walker['index'] + 1

                    index = index + 1
        except Exception as error:
            print(f'error: {error} / dictlist.run_walker()')
