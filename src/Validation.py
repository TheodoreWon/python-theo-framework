class Validation:
    @staticmethod
    def validate_name(name):
        if not isinstance(name, str):
            raise AssertionError('name(type:{}) should be str.'.format(type(name)))

    """
    Validation functions for DictList
    """

    @staticmethod
    def validate_datum(key, datum):
        if not isinstance(datum, dict):
            raise AssertionError('datum(type:{}) should be dict.'.format(type(datum)))

        if key is not None and key not in datum:
            raise AssertionError('datum(keys:{}) does not have the key({}).'.format(list(datum.keys()), key))

    @staticmethod
    def validate_data(key, data):
        if not isinstance(data, list):
            raise AssertionError('data(type:{}) should be list.'.format(type(data)))

        if key is not None:
            for datum in data:
                if key not in datum:
                    raise AssertionError('datum(keys:{}) does not have the key({}).'.format(list(datum.keys()), key))

    @staticmethod
    def validate_dictlist(key, dictlist):
        from .DictList import DictList
        if not isinstance(dict, DictList):
            raise AssertionError('dictlist(type:{}) should be DictList.'.format(type(dictlist)))

        Validation.validate_data(key, dictlist.get_data())

    @staticmethod
    def validate_filters(filters):
        if filters is not None:
            if not isinstance(filters, list):
                raise AssertionError('filters(type:{}) should be list.'.format(type(filters)))

            for filter in filters:
                if not isinstance(filter, dict):
                    raise AssertionError('filter(type:{}) should be dict.'.format(type(filter)))

                if not ('key' in filter and 'value' in filter):
                    raise AssertionError('filter(keys:{}) does not have key or value.'.format(list(filter.keys())))

    @staticmethod
    def validate_file(file):
        if not isinstance(file, str):
            raise AssertionError('file(type:{}) should be str.'.format(type(file)))

    """
    Validation functions for MongoDB
    """
    @staticmethod
    def validate_mongodb(database, collection):
        if not isinstance(database, str):
            raise AssertionError('database(type:{}) should be str.'.format(type(database)))

        if not isinstance(collection, str):
            raise AssertionError('collection(type:{}) should be str.'.format(type(collection)))

    @staticmethod
    def validate_range(range):
        if range is not None:
            if not isinstance(range, dict):
                raise AssertionError('range(type:{}) should be dict.'.format(type(range)))

            if not ('key' in range and ('min' in range or 'max' in range)):
                raise AssertionError('range(keys:{}) does not have key or min, max.'.format(list(filter.keys())))

    """
    Validation functions for Telegram
    """
    @staticmethod
    def validate_room(room):
        if not isinstance(room, dict):
            raise AssertionError('room(type:{}) should be dict.'.format(type(room)))

        if not ('id' in room and 'type' in room):
            raise AssertionError('room(keys:{}) does not have id or type.'.format(list(room.keys())))

    @staticmethod
    def validate_message(message):
        if not isinstance(message, dict):
            raise AssertionError('message(type:{}) should be dict.'.format(type(message)))

        if not ('id' in message and 'type' in message and 'contents' in message):
            raise AssertionError('message(keys:{}) does not have id or type or contents.'.format(list(message.keys())))

    @staticmethod
    def validate_chat(chat):
        if not isinstance(chat, dict):
            raise AssertionError('chat(type:{}) should be dict.'.format(type(chat)))

        if not ('room' in chat and 'message' in chat):
            raise AssertionError('chat(keys:{}) does not have room or message.'.format(list(chat.keys())))

        Validation.validate_room(chat['room'])
        Validation.validate_message(chat['message'])
