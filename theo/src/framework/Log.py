import logging
import os
import datetime
import shutil
from theo.src.framework.DictList import DictList


class Log:
    """
    Log is made to log a program by printing and storing.
    Log works with the configurations.

    When Log works with new name and new level, configuration files are stored the data as JSON.
    File locations are set from configurations.
    By the configuration, printing and storing work by level comparison.
    If value of argument level is higher than value of name's level, the print function works.

    The default levels are critical(100), info(50), debug(30), none(0).
    And the default configuration is Print(info), Store(debug).
    If the configuration is not changed, the log what is set a level higher than info is printed and debug is stored.

    Initially, the storing does not work.
    To store a log, calling configure(store_enabled=True) is needed before construct Log class.

    Methods:
        configure(print_enabled=None, store_enabled=None,
                  config_directory=None, log_directory=None,
                  over_time_log_clear_enabled=None, days_over_time=None)
        log = Log(name)
        print(level, *messages)

    Example:
        from theo.framework import Log

        Log.configure(print_enabled=True, store_enabled=True, over_time_log_clear_enabled=True)
        log = Log('name')
        log.print('info', 'Hello, theo.framework!')
    """

    is_started = False

    print_logger = None
    store_logger = None

    name_config_dictlist = DictList(key='name')
    level_config_dictlist = DictList(key='level')

    """
    Configurations for Log
    1. Enable print or store
    2. Config directory
    3. Log directory
    4. Automated clearing log data feature
    """
    print_enabled = True
    store_enabled = False

    config_directory = os.path.join(os.getcwd(), 'configs', 'log')
    name_config_path = os.path.join(config_directory, 'name_config.json')
    level_config_path = os.path.join(config_directory, 'level_config.json')

    log_directory = os.path.join(os.getcwd(), 'files', 'log')
    log_store_directory = os.path.join(log_directory, datetime.datetime.now().strftime('%Y-%m-%d'))

    over_time_log_clear_enabled = False
    days_over_time = 2

    @staticmethod
    def configure(print_enabled=None, store_enabled=None,
                  config_directory=None, log_directory=None,
                  over_time_log_clear_enabled=None, days_over_time=None):
        if not Log.is_started:
            if print_enabled is not None:
                if not isinstance(print_enabled, bool):
                    raise AssertionError(
                        '[theo.framework.Log] error: print_enabled(type:{}) should be bool.'.format(
                            type(print_enabled)))

                Log.print_enabled = print_enabled

            if store_enabled is not None:
                if not isinstance(store_enabled, bool):
                    raise AssertionError(
                        '[theo.framework.Log] error: store_enabled(type:{}) should be bool.'.format(
                            type(store_enabled)))

                Log.store_enabled = store_enabled

            if config_directory is not None:
                if not isinstance(config_directory, str):
                    raise AssertionError(
                        '[theo.framework.Log] error: config_directory(type:{}) should be str.'.format(
                            type(config_directory)))

                Log.config_directory = config_directory
                Log.name_config_path = os.path.join(Log.config_directory, 'name_config.json')
                Log.level_config_path = os.path.join(Log.config_directory, 'level_config.json')

            if log_directory is not None:
                if not isinstance(log_directory, str):
                    raise AssertionError(
                        '[theo.framework.Log] error: log_directory(type:{}) should be str.'.format(type(log_directory)))

                Log.log_directory = log_directory
        else:
            raise AssertionError('[theo.framework.Log] error: config should be configured before using.')
            # print('[theo.framework.Log] warning: config should be configured before using.')

    @staticmethod
    def print_config():
        print('[theo.framework.Log] print configuration')
        print('- Enabled')
        print('    Print : {}'.format(Log.print_enabled))
        print('    Store : {}'.format(Log.store_enabled))
        print('- Directories')
        print('    Config : {}'.format(Log.config_directory))
        print('    Log    : {}'.format(Log.log_directory))
        print('- Options')
        print('    Over time log clear : Enabled({}) Days({})'.format(Log.over_time_log_clear_enabled,
                                                                      Log.days_over_time))

    def __init__(self, name):
        if not isinstance(name, str):
            raise AssertionError('[theo.framework.Log] error: name(type:{}) should be str.'.format(type(name)))

        Log.initial()

        self.name = name
        self.level_config = Log.get_level_config(self.name)

    def print(self, level, *messages):
        log = '[{}][{}] '.format(self.name, level)
        for message in messages:
            log += str(message)

        level_value = Log.get_level_value(level)
        if Log.print_logger is not None and level_value >= Log.get_level_value(self.level_config['print']):
            Log.print_logger.info(log)

        if Log.store_logger is not None and level_value >= Log.get_level_value(self.level_config['store']):
            Log.store_logger.info(log)

    @staticmethod
    def initial():
        if not Log.is_started:
            Log.print_config()

            # configuration files
            if not os.path.exists(Log.config_directory):
                os.makedirs(Log.config_directory)

            if os.path.exists(Log.name_config_path):
                Log.name_config_dictlist.import_json(Log.name_config_path)

            if not os.path.exists(Log.level_config_path):
                Log.level_config_dictlist.extend_data([
                    {'level': 'critical', 'value': 100},
                    {'level': 'info', 'value': 50},
                    {'level': 'debug', 'value': 30},
                    {'level': 'none', 'value': 0},
                ])
                Log.level_config_dictlist.export_json(Log.level_config_path)
            else:
                Log.level_config_dictlist.import_json(Log.level_config_path)

            # loggers
            if Log.print_enabled:
                Log.print_logger = logging.getLogger('print')
                Log.print_logger.setLevel(logging.INFO)

                print_stream_handler = logging.StreamHandler()
                print_stream_handler.setFormatter(logging.Formatter('[%(asctime)s]%(message)s'))
                Log.print_logger.addHandler(print_stream_handler)

            if Log.store_enabled:
                if not os.path.exists(Log.log_directory):
                    os.makedirs(Log.log_directory)

                if Log.over_time_log_clear_enabled:
                    for (path, directories, files) in os.walk(Log.log_directory):
                        for directory in directories:
                            if Log.days_over_time <= \
                               (datetime.datetime.now() - datetime.datetime.strptime(directory, '%Y-%m-%d')).days:
                                shutil.rmtree(os.path.join(Log.log_directory, directory))

                        break

                Log.log_store_directory = os.path.join(Log.log_directory, datetime.datetime.now().strftime('%Y-%m-%d'))
                if not os.path.exists(Log.log_store_directory):
                    os.makedirs(Log.log_store_directory)

                Log.store_logger = logging.getLogger('store')
                Log.store_logger.setLevel(logging.INFO)

                file_handler = logging.FileHandler(
                    os.path.join(Log.log_store_directory, datetime.datetime.now().strftime('%H-%M-%S.log')))
                file_handler.setFormatter(logging.Formatter('[%(asctime)s]%(message)s'))
                Log.store_logger.addHandler(file_handler)

            Log.is_started = True

    @staticmethod
    def get_level_config(name):
        name_config = Log.name_config_dictlist.get_datum(name)

        if name_config is None:
            Log.name_config_dictlist.append({'name': name, 'print': 'info', 'store': 'debug'})
            name_config = Log.name_config_dictlist.get_datum(name)
            Log.name_config_dictlist.export_json(Log.name_config_path)

        return name_config

    @staticmethod
    def get_level_value(level):
        level_config = Log.level_config_dictlist.get_datum(level)

        if level_config is None:
            Log.level_config_dictlist.append({'level': level, 'value': 50})
            level_config = Log.level_config_dictlist.get_datum(level)
            Log.level_config_dictlist.export_json(Log.level_config_path)

        return level_config['value']
