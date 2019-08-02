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
        Log.configure(print_enabled=None, store_enabled=None, config_directory=None, log_directory=None,
                      over_time_log_clear_enabled=None, over_time_days=None)
        log = Log(name)
        log.print(level, message)

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

    print_enabled = True
    store_enabled = False

    config_directory = os.path.join(os.getcwd(), 'configs', 'log')
    name_config_path = os.path.join(config_directory, 'name_config.json')
    level_config_path = os.path.join(config_directory, 'level_config.json')

    log_directory = os.path.join(os.getcwd(), 'files', 'log')
    log_store_directory = os.path.join(log_directory, datetime.datetime.now().strftime('%Y-%m-%d'))

    over_time_log_clear_enabled = False
    over_time_days = 3

    @staticmethod
    def configure(print_enabled=None, store_enabled=None,
                  config_directory=None, log_directory=None,
                  over_time_log_clear_enabled=None, over_time_days=None):
        try:
            if not Log.is_started:
                Log.print_enabled = True if print_enabled else Log.print_enabled
                Log.store_enabled = True if store_enabled else Log.store_enabled

                Log.config_directory = config_directory if config_directory else Log.config_directory
                Log.name_config_path = os.path.join(Log.config_directory, 'name_config.json') if config_directory else Log.name_config_path
                Log.level_config_path = os.path.join(Log.config_directory, 'level_config.json') if config_directory else Log.level_config_path
                Log.log_directory = log_directory if log_directory else Log.log_directory

                Log.over_time_log_clear_enabled = True if over_time_log_clear_enabled else Log.over_time_log_clear_enabled
                Log.over_time_days = over_time_days if over_time_days else Log.over_time_days
        except Exception as error:
            print(f'error: {error} / Log.configure(print_enabled:{print_enabled}/{type(print_enabled)}, store_enabled:{store_enabled}/{type(store_enabled)},')
            print(f'       config_directory:{config_directory}/{type(config_directory)}, log_directory:{log_directory}/{type(log_directory)}'
                  + f', over_time_log_clear_enabled:{over_time_log_clear_enabled}/{type(over_time_log_clear_enabled)}, over_time_days:{over_time_days}/{type(over_time_days)}')

    def __init__(self, name):
        try:
            self.name = name

            if not Log.is_started:
                print(f'Log Enabled(print:{Log.print_enabled}, store:{Log.store_enabled})')
                print(f'Log Directories(config:{Log.config_directory}' + (f', log:{Log.log_directory})' if Log.store_enabled else ')'))
                if Log.store_enabled:
                    print(f'Log Option(over_time_log_clear_enabled:{Log.over_time_log_clear_enabled},',
                          f'days:{Log.over_time_days})' if Log.over_time_log_clear_enabled else ')')

                if not os.path.exists(Log.config_directory):
                    os.makedirs(Log.config_directory)

                if os.path.exists(Log.name_config_path):
                    Log.name_config_dictlist.import_json(Log.name_config_path)

                if not os.path.exists(Log.level_config_path):
                    Log.level_config_dictlist.append({'level': 'critical', 'value': 100})
                    Log.level_config_dictlist.append({'level': 'info', 'value': 50})
                    Log.level_config_dictlist.append({'level': 'debug', 'value': 30})
                    Log.level_config_dictlist.append({'level': 'none', 'value': 0})

                    Log.level_config_dictlist.export_json(Log.level_config_path)
                else:
                    Log.level_config_dictlist.import_json(Log.level_config_path)

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
                        for directory in os.listdir(Log.log_directory):
                            if os.path.isdir(os.path.join(Log.log_directory, directory)) \
                                and (Log.over_time_days <= (datetime.datetime.now() - datetime.datetime.strptime(directory, '%Y-%m-%d')).days):
                                    shutil.rmtree(os.path.join(Log.log_directory, directory))

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

            self.level_config = Log.name_config_dictlist.get(name)
            if not self.level_config:
                self.level_config = {'name': name, 'print': 'info', 'store': 'debug'}

                Log.name_config_dictlist.append(self.level_config)
                Log.name_config_dictlist.export_json(Log.name_config_path)
        except Exception as error:
            print(f'error: {error} / Log(name:{name}/{type(name)})')

    @staticmethod
    def get_level_value(level):
        try:
            level_config = Log.level_config_dictlist.get(level)

            if not level_config:
                level_config = {'level': level, 'value': 50}

                Log.level_config_dictlist.append(level_config)
                Log.level_config_dictlist.export_json(Log.level_config_path)

            return level_config['value']
        except Exception as error:
            print(f'error: {error} / Log.get_level_value(level:{level}/{type(level)})')
            return 50

    def print(self, level, *messages):
        try:
            log = f'[{self.name}][{level}]'
            for message in messages:
                log += ' ' + str(message)

            level_value = Log.get_level_value(level)

            if Log.print_logger and level_value >= Log.get_level_value(self.level_config['print']):
                Log.print_logger.info(log)

            if Log.store_logger and level_value >= Log.get_level_value(self.level_config['store']):
                Log.store_logger.info(log)
        except Exception as error:
            print(f'error: {error} / log.print(level:{level}/{type(level)}, message:{message}/{type(message)})')
