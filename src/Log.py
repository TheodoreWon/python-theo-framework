import logging
import os
import datetime
import shutil

from .DictList import DictList


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
        log.print('info', 'Hello, theo library.')
    """
    name_config_dictlist, level_config_dictlist = None, None
    print_logger, store_logger = None, None

    def __init__(self, name):
        self.config()

        self.name = name
        self.level_config = self.get_level_config(self.name)

    def print(self, level, *messages):
        log = '[{}][{}] '.format(self.name, level)
        for message in messages:
            log += str(message)

        level_value = self.get_level_value(level)
        if print_enabled and level_value >= self.get_level_value(self.level_config['print']):
            self.print_logger.info(log)

        if store_enabled and level_value >= self.get_level_value(self.level_config['store']):
            self.store_logger.info(log)

    """
    Internal configuration functions
    """
    def config(self):
        if not os.path.exists(config_directory):
            os.makedirs(config_directory)

        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        if self.name_config_dictlist is None:
            self.name_config_dictlist = DictList(key='name')

            if os.path.exists(name_config_file):
                self.name_config_dictlist.import_json(name_config_file)

        if self.level_config_dictlist is None:
            self.level_config_dictlist = DictList(key='level')

            if os.path.exists(level_config_file):
                self.level_config_dictlist.import_json(level_config_file)

        if days_over_time > 0:
            for log_date_directory in os.listdir(log_root_directory):
                if days_over_time \
                        <= (datetime.datetime.now() - datetime.datetime.strptime(log_date_directory, '%Y-%m-%d')).days:
                    shutil.rmtree(os.path.join(log_root_directory, log_date_directory))

        if print_enabled and self.print_logger is None:
            self.print_logger = logging.getLogger('print')
            self.print_logger.setLevel(logging.INFO)

            print_stream_handler = logging.StreamHandler()
            print_stream_handler.setFormatter(logging.Formatter('[%(asctime)s]%(message)s'))
            self.print_logger.addHandler(print_stream_handler)

        if store_enabled and self.store_logger is None:
            self.store_logger = logging.getLogger('store')
            self.store_logger.setLevel(logging.INFO)

            file_handler = logging.FileHandler(
                os.path.join(log_directory, datetime.datetime.now().strftime('%H-%M-%S.log')))
            file_handler.setFormatter(logging.Formatter('[%(asctime)s]%(message)s'))
            self.store_logger.addHandler(file_handler)

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
