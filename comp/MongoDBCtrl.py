import sys
sys.path.append('..')

from src.Component import Component
from src.System import system


class MongoDBCtrl(Component):
    def set_related_components(self):
        self.related_components.clear()

    def initial(self):
        self.log.print('info', 'initial (related:{})'.format(self.related_components))

        from src.MongoDB import MongoDB
        self.db_handler = MongoDB()

        system.register_interface(self.name, 'get_databases', [0], self.get_databases)
        system.register_interface(self.name, 'get_collections', [1], self.get_collections)
        system.register_interface(self.name, 'is_database_exist', [1], self.is_database_exist)
        system.register_interface(self.name, 'is_collection_exist', [2], self.is_collection_exist)

        system.register_interface(self.name, 'drop_database', [1], self.drop_database)
        system.register_interface(self.name, 'drop_collection', [2], self.drop_collection)

        system.register_interface(self.name, 'save_data', [3, 4], self.save_data)
        system.register_interface(self.name, 'load_data', [2, 3, 4, 5], self.load_data)
        system.register_interface(self.name, 'get_keys', [2], self.get_keys)
        system.register_interface(self.name, 'get_range', [3], self.get_range)

    def get_databases(self):
        return self.db_handler.get_databases()

    def get_collections(self, database):
        return self.db_handler.get_collections(database)

    def is_database_exist(self, database):
        return self.db_handler.is_database_exist(database)

    def is_collection_exist(self, database, collection):
        return self.db_handler.is_collection_exist(database, collection)

    def drop_database(self, database):
        if self.is_database_exist(database):
            self.log.print('info', 'drop_database(database:{})'.format(database))
            self.db_handler.drop_database(database)
        else:
            self.log.print('info', 'database({}) is not exist.'.format(database))

    def drop_collection(self, database, collection):
        if self.is_collection_exist(database, collection):
            self.log.print('info', 'drop_collection(database:{}/collection:{})'.format(database, collection))
            self.db_handler.drop_collection(database, collection)
        else:
            self.log.print('info', 'target(database:{}/collection:{}) is not exist.'.format(database, collection))

    def save_data(self, database, collection, data, unique_key=None):
        self.db_handler.save_data(database, collection, data, unique_key)

    def load_data(self, database, collection, sorting_key=None, keys=None, range=None):
        return self.db_handler.load_data(database, collection, sorting_key, keys, range)

    def get_keys(self, database, collection):
        return self.db_handler.get_keys(database, collection)

    def get_range(self, database, collection, key):
        return self.db_handler.get_range(database, collection, key)
