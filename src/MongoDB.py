import pymongo

from .Validation import Validation


class MongoDB:
    """
    MongoDB supports the functionality to mangage a database.

    Pre-condition:
        pip install pymongo

    Methods:
        Mongo()

        get_databases()
        get_collections(database)
        is_database_exist(database)
        is_collection_exist(database, collection)

        drop_database(database)
        drop_collection(database, collection)

        save_data(database, collection, data, unique_key)
        load_data(database, collection, sorting_key=None, keys=None, range=None)
        get_keys(database, collection)
        get_range(database, collection, key)

    Arguments:
        range (range dictionary): key, min(option), max(option)
    """

    def __init__(self):
        self.client = pymongo.MongoClient()

        try:
            self.client.admin.command('ismaster')
        except pymongo.errors.ServerSelectionTimeoutError:
            self.client = None
            raise AssertionError('[MongoDB] The client is not ready.')

    def __del__(self):
        if self.client is not None:
            self.client.close()

    def get_databases(self):
        return list(self.client.database_names())

    def get_collections(self, database):
        return list(self.client[database].collection_names())

    def is_database_exist(self, database):
        return True if database in self.client.database_names() else False

    def is_collection_exist(self, database, collection):
        Validation.validate_mongodb(database, collection)

        return True if collection in self.client[database].collection_names() else False

    def drop_database(self, database):
        self.client.drop_database(database)

    def drop_collection(self, database, collection):
        Validation.validate_mongodb(database, collection)

        self.client[database].drop_collection(collection)

    def save_data(self, database, collection, data, unique_key=None):
        Validation.validate_mongodb(database, collection)

        if self.is_collection_exist(database, collection):
            if unique_key is None:
                try:
                    self.client[database][collection].insert_many(data)
                except pymongo.errors.BulkWriteError:
                    raise AssertionError('[MongoDB] Fail to save data, because of the duplication.')
            else:
                for datum in data:
                    self.client[database][collection].find_one_and_update(
                        {unique_key: datum[unique_key]}, {'$set': datum}, upsert=True)
        else:
            if unique_key is not None:
                self.client[database][collection].create_index([(unique_key, pymongo.ASCENDING)], unique=True)

            try:
                self.client[database][collection].insert_many(data)
            except pymongo.errors.BulkWriteError:
                raise AssertionError('[MongoDB] Fail to save data, because of the duplication.')

    def load_data(self, database, collection, sorting_key=None, keys=None, range=None):
        Validation.validate_mongodb(database, collection)

        if not self.is_collection_exist(database, collection):
            return list()

        from .Validation import Validation
        Validation.validate_range(range)

        range_condition = dict()

        if range is not None:
            if 'min' in range:
                range_condition['$gte'] = range.get('min')

            if 'max' in range:
                range_condition['$lte'] = range.get('max')

        cursor = self.client[database][collection].find(
            sort=None if sorting_key is None else [(sorting_key, pymongo.ASCENDING)],
            projection=self.get_projection(keys),
            filter=None if range is None else {range.get('key'): range_condition})

        return list(cursor)

    def get_keys(self, database, collection):
        Validation.validate_mongodb(database, collection)

        return list() if not self.is_collection_exist(database, collection) \
            else list(self.client[database][collection].find_one(projection=self.get_projection()).keys())

    def get_range(self, database, collection, key):
        Validation.validate_mongodb(database, collection)

        if not self.is_collection_exist(database, collection):
            return None

        start = self.client[database][collection].find_one(
            projection=self.get_projection([key]), sort=[(key, pymongo.ASCENDING)])
        end = self.client[database][collection].find_one(
            projection=self.get_projection([key]), sort=[(key, pymongo.DESCENDING)])

        if key not in start or key not in end:
            return None

        return {'key': key, 'start': start[key], 'end': end[key]}

    @staticmethod
    def get_projection(keys=None):
        projection = {'_id': False}

        if keys is None:
            keys = {}

        for key in keys:
            projection[key] = True

        return projection
