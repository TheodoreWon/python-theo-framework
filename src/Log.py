import logging
import os
import datetime
import shutil

from .Validation import Validation


"""
Configurations for Log
1. Enable print or store
2. Config directory and files
3. Log directory and files
4. Automated clearing log data feature
"""
print_enabled = True
store_enabled = False

config_directory = os.path.join(os.getcwd(), 'configs', 'log')
name_config_file = os.path.join(config_directory, 'name_config.json')
level_config_file = os.path.join(config_directory, 'level_config.json')

log_root_directory = os.path.join(os.getcwd(), 'files', 'log')
log_directory = os.path.join(log_root_directory, datetime.datetime.now().strftime('%Y-%m-%d'))

days_over_time = 2  # 0 : never clear log data

default_level = 'default'
default_level_value = 50

print_logger = None
store_logger = None


class Log:
    """
    Log is made to log a program by printing and storing.
    Log works with the configuration what is set in this file first.

    When Log works with new name and new level, configuration files store the data as JSON file.
    file locations are set from configurations.
    By the configuration, printing and storing work by level comparison.
    If value of argument level is higher than value of name's level, the print function works.

    Methods:
        log = Log(name)
        print(level, *messages)

    Example:
        log = Log('name')
        log.print('info', 'Hello, python-library.')
    """
    from .DictList import DictList
    name_config_dictlist = DictList(key='name')
    level_config_dictlist = DictList(key='level')

    def __init__(self, name):
        Validation.validate_name(name)

        self.config()

        self.name = name
        self.level_config = self.get_level_config(self.name)

    def print(self, level, *messages):
        log = '[{}][{}] '.format(self.name, level)
        for message in messages:
            log += str(message)

        level_value = self.get_level_value(level)
        if print_logger is not None and level_value >= self.get_level_value(self.level_config['print']):
            print_logger.info(log)

        if store_logger is not None and level_value >= self.get_level_value(self.level_config['store']):
            store_logger.info(log)

    """
    Internal configuration functions
    """
    def config(self):
        if not os.path.exists(config_directory):
            os.makedirs(config_directory)

        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        if self.name_config_dictlist.count() == 0 and os.path.exists(name_config_file):
            self.name_config_dictlist.import_json(name_config_file)

        if self.level_config_dictlist.count() == 0 and os.path.exists(level_config_file):
            self.level_config_dictlist.import_json(level_config_file)

        if days_over_time > 0:
            for log_date_directory in os.listdir(log_root_directory):
                if days_over_time \
                        <= (datetime.datetime.now() - datetime.datetime.strptime(log_date_directory, '%Y-%m-%d')).days:
                    shutil.rmtree(os.path.join(log_root_directory, log_date_directory))

        global print_logger
        if print_enabled and print_logger is None:
            print_logger = logging.getLogger('print')
            print_logger.setLevel(logging.INFO)

            print_stream_handler = logging.StreamHandler()
            print_stream_handler.setFormatter(logging.Formatter('[%(asctime)s]%(message)s'))
            print_logger.addHandler(print_stream_handler)

        global store_logger
        if store_enabled and store_logger is None:
            store_logger = logging.getLogger('store')
            store_logger.setLevel(logging.INFO)

            file_handler = logging.FileHandler(
                os.path.join(log_directory, datetime.datetime.now().strftime('%H-%M-%S.log')))
            file_handler.setFormatter(logging.Formatter('[%(asctime)s]%(message)s'))
            store_logger.addHandler(file_handler)

    def get_level_config(self, name):
        name_config = self.name_config_dictlist.get_datum(name)

        if name_config is None:
            self.name_config_dictlist.append({'name': name, 'print': default_level, 'store': default_level})
            name_config = self.name_config_dictlist.get_datum(name)
            self.name_config_dictlist.export_json(name_config_file)

        return name_config

    def get_level_value(self, level):
        level_config = self.level_config_dictlist.get_datum(level)

        if level_config is None:
            self.level_config_dictlist.append({'level': level, 'value': default_level_value})
            level_config = self.level_config_dictlist.get_datum(level)
            self.level_config_dictlist.export_json(level_config_file)

        return level_config['value']
