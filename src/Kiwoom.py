import sys
import time
import datetime
import copy
import PyQt5

from .Validation import Validation


"""
Configurations for Kiwoom
1. Waiting type for the limitation of TR request : 1 (minimum time gap) or 2 (limitation number)
"""
tr_request_waiting_type = 1


class Kiwoom(PyQt5.QAxContainer.QAxWidget):
    """
    Kiwoom provides the functionality to control Kiwoom API.
    To use the Kiwoom API, it is obligation to setup the Kiwoom API environment.

    TODO: It is not tested. It should be tested with a project use.

    Methods:
        Kiwoom()
        get_accounts()
        get_markets()
        get_codes(market)
        get_price_types(market, code)
        get_item(market, code)
        get_prices(market, code, price_type, range=None)
    """

    from .DictList import DictList
    tran_dictlist = DictList('separator')
    market_dictlist = DictList('market')
    error_dictlist = DictList('code')

    def __init__(self):
        from .Log import Log
        self.log = Log('Lib-Kiwoom')

        self.config()

        self.q_application = PyQt5.QtWidgets.QApplication(sys.argv)
        super().__init__()
        self.setControl('KHOPENAPI.KHOpenAPICtrl.1')

        self.event_wait_on_event_connect = None
        self.event_wait_on_receive_tr_data = None
        self.connect_events()

        self.tr_is_chain_data = False
        self.tr_internal_data = None

        while not self.GetConnectState():
            self.CommConnect()

    def get_accounts(self):
        accounts = self.GetLoginInfo('ACCNO').split(';')
        accounts.remove('')
        return accounts

    def get_markets(self):
        return self.market_dictlist.get_values('market')

    def get_codes(self, market):
        market = self.market_dictlist.get_data(market)
        if market is not None:
            if 'codes' not in market:
                codes = self.GetCodeListByMarket(market['code']).split(';')
                codes.remove('')
                market['codes'] = codes

            return copy.copy(market['codes'])

        return None

    def get_price_types(self, market, code):
        if code in self.get_codes(market):
            return ['month', 'week', 'day', 'min+30', 'min+1']

        return None

    def get_item(self, market, code):
        if code in self.get_codes(market):
            tran_data_list = self.get_tran_data_list('get_item', [code])
            return tran_data_list[0] if len(tran_data_list) else None

        return None

    def get_prices(self, market, code, price_type, range=None):
        Validation.validate_range(range)

        if code in self.get_codes(market):
            start = '19700101' if range is None or 'start' not in range \
                else datetime.strftime(range['start'], '%Y%m%d')
            end = datetime.strftime(datetime.now(), '%Y%m%d') if range is None or 'end' not in range \
                else datetime.strftime(range['end'], '%Y%m%d')

            self.log.print(
                'info', 'get_price_list(market:{}/code:{}/price_type:{}/range:{})'.format(
                    market, code, price_type, range) + '/(start:{}/end:{})'.format(start, end))

            if 'month' == price_type:
                return self.get_tran_data_list('get_month_prices', [code, end, start, '0'], range)
            elif 'week' == price_type:
                return self.get_tran_data_list('get_week_prices', [code, end, start, '0'], range)
            elif 'day' == price_type:
                return self.get_tran_data_list('get_day_prices', [code, end, '0'], range)
            elif 'min' in price_type:
                return self.get_tran_data_list('get_minute_prices', [code, price_type.split('+')[1], '0'], range)

        return None

    def get_tran_data_list(self, separator, arguments, range=None):
        tran = self.tran_dictlist(separator)

        if tran is None:
            self.log.print('critical', 'separator({}) is not supported.'.format(separator))

        if len(arguments) != len(tran['arguments']):
            self.log.print(
                'critical', 'arguments({}) is not match with the table for separator({})'.format(arguments, separator))

        for index, item in enumerate(tran['arguments']):
            self.SetInputValue(item, arguments[index])

        data = list()
        result, is_chain_data, internal_data = self.CommRqData(separator, tran['code'], 0, tran['screen'])
        request_count = 1

        if result == 0:
            if self.remove_over_range_data(internal_data, range):
                is_chain_data = False

            data.extend(copy.copy(internal_data))

            while is_chain_data:
                for index, item in enumerate(tran['arguments']):
                    self.SetInputValue(item, arguments[index])

                result, is_chain_data, internal_data = self.CommRqData(separator, tran['code'], 2, tran['screen'])

                request_count = request_count + 1
                if 0 == (request_count % 5):
                    self.log.print('info', 'Request TR is working in chain(count:{})'.format(request_count))

                if result == 0:
                    if self.remove_over_range_data(internal_data, range):
                        is_chain_data = False

                    data.extend(copy.copy(internal_data))
                else:
                    is_chain_data = False

        return data

    @staticmethod
    def remove_over_range_data(data, range):
        if range is not None:
            start = range['start'] if 'start' in range else None
            end = range['end'] if 'end' in range else None

            over_range_data = list()
            for datum in data:
                if start is not None and datum['datetime'] < start:
                    over_range_data.append(datum)
                elif end is not None and datum['datetime'] > end:
                    over_range_data.append(datum)

            if len(over_range_data) != 0:
                for over_range_datum in over_range_data:
                    over_range_data.remove(over_range_datum)

                return True

        return False

    """
    Internal configuration functions

    config()
    config_tran()
    config_market()
    config_error()
    """
    def config(self):
        self.config_tran()
        self.config_market()
        self.config_error()

    def config_tran(self):
        if self.tran_dictlist.count() == 0:
            self.tran_dictlist.extend_data([
                {
                    'separator': 'get_item',
                    'code': 'opt10001',
                    'screen': '1001',
                    'type': 'data',
                    'data_type': 'single',
                    'arguments': ['종목코드'],
                    'results': [
                        ['종목코드', 'code', 'str'],
                        ['시가총액', 'market capitalization', 'float'],
                        ['250최고', '250 days high', 'float'],
                        ['250최저', '250 days low', 'float'],
                        ['PBR', 'pbr', 'float'],
                        ['PER', 'per', 'float'],
                        ['ROE', 'roe', 'float'],
                        ['EPS', 'eps', 'float'],
                        ['매출액', 'net sales', 'float'],
                        ['영업이익', 'operating profit', 'float'],
                        ['당기순이익', 'net profit', 'float']
                    ]
                },
                {
                    'separator': 'get_minute_prices',
                    'code': 'opt10080',
                    'screen': '1501',
                    'type': 'data',
                    'data_type': 'multi',
                    'arguments': ['종목코드', '틱범위', '수정주가구분'],
                    'results': [
                        ['체결시간', 'datetime', 'datetime'],
                        ['시가', 'open', 'float'],
                        ['현재가', 'close', 'float'],
                        ['고가', 'high', 'float'],
                        ['저가', 'low', 'float'],
                        ['거래량', 'volume', 'float']
                    ]
                },
                {
                    'separator': 'get_day_prices',
                    'code': 'opt10081',
                    'screen': '1502',
                    'type': 'data',
                    'data_type': 'multi',
                    'arguments': ['종목코드', '기준일자', '수정주가구분'],
                    'results': [
                        ['일자', 'datetime', 'datetime'],
                        ['시가', 'open', 'float'],
                        ['현재가', 'close', 'float'],
                        ['고가', 'high', 'float'],
                        ['저가', 'low', 'float'],
                        ['거래량', 'volume', 'float']
                    ]
                },
                {
                    'separator': 'get_week_prices',
                    'code': 'opt10082',
                    'screen': '1503',
                    'type': 'data',
                    'data_type': 'multi',
                    'arguments': ['종목코드', '기준일자', '끝일자', '수정주가구분'],
                    'results': [
                        ['일자', 'datetime', 'datetime'],
                        ['시가', 'open', 'float'],
                        ['현재가', 'close', 'float'],
                        ['고가', 'high', 'float'],
                        ['저가', 'low', 'float'],
                        ['거래량', 'volume', 'float']
                    ]
                },
                {
                    'separator': 'get_month_prices',
                    'code': 'opt10083',
                    'screen': '1504',
                    'type': 'data',
                    'data_type': 'multi',
                    'arguments': ['종목코드', '기준일자', '끝일자', '수정주가구분'],
                    'results': [
                        ['일자', 'datetime', 'datetime'],
                        ['시가', 'open', 'float'],
                        ['현재가', 'close', 'float'],
                        ['고가', 'high', 'float'],
                        ['저가', 'low', 'float'],
                        ['거래량', 'volume', 'float']
                    ]
                }
            ])

    def config_market(self):
        if self.market_dictlist.count() == 0:
            self.market_dictlist.extend_data([
                {'code': 0, 'market': 'kospi'},
                {'code': 10, 'market': 'kosdaq'},

                # {'code': 3, 'market': 'ELW'},
                # {'code': 4, 'market': '뮤추얼펀드'},
                # {'code': 5, 'market': '신주인수권'},
                # {'code': 6, 'market': '리츠'},
                # {'code': 8, 'market': 'ETF'},
                # {'code': 9, 'market': '하이일드펀드'},
                # {'code': 30, 'market': 'K-OTC'},
                # {'code': 50, 'market': '코넥스(KONEX)'}
            ])

    def config_error(self):
        if self.error_dictlist.count() == 0:
            self.error_dictlist.extend_data([
                {'code': 0, 'error': 'OP_ERR_NONE'},
                {'code': -10, 'error': 'OP_ERR_FAIL'},
                {'code': -100, 'error': 'OP_ERR_LOGIN'},
                {'code': -101, 'error': 'OP_ERR_CONNECT'},
                {'code': -102, 'error': 'OP_ERR_VERSION'},
                {'code': -103, 'error': 'OP_ERR_FIREWALL'},
                {'code': -104, 'error': 'OP_ERR_MEMORY'},
                {'code': -105, 'error': 'OP_ERR_INPUT'},
                {'code': -106, 'error': 'OP_ERR_SOCKET_CLOSED'},
                {'code': -200, 'error': 'OP_ERR_SISE_OVERFLOW'},
                {'code': -201, 'error': 'OP_ERR_RQ_STRUCT_FAIL'},
                {'code': -202, 'error': 'OP_ERR_RQ_STRING_FAIL'},
                {'code': -203, 'error': 'OP_ERR_NO_DATA'},
                {'code': -204, 'error': 'OP_ERR_OVER_MAX_DATA'},
                {'code': -205, 'error': 'OP_ERR_DATA_RCV_FAIL'},
                {'code': -206, 'error': 'OP_ERR_OVER_MAX_FID'},
                {'code': -207, 'error': 'OP_ERR_REAL_CANCEL'},
                {'code': -300, 'error': 'OP_ERR_ORD_WRONG_INPUT'},
                {'code': -301, 'error': 'OP_ERR_ORD_WRONG_ACCTNO'},
                {'code': -302, 'error': 'OP_ERR_OTHER_ACC_USE'},
                {'code': -303, 'error': 'OP_ERR_MIS_2BILL_EXC'},
                {'code': -304, 'error': 'OP_ERR_MIS_5BILL_EXC'},
                {'code': -305, 'error': 'OP_ERR_MIS_1PER_EXC'},
                {'code': -306, 'error': 'OP_ERR_MIS_3PER_EXC'},
                {'code': -307, 'error': 'OP_ERR_SEND_FAIL'},
                {'code': -308, 'error': 'OP_ERR_ORD_OVERFLOW'},
                {'code': -309, 'error': 'OP_ERR_MIS_300CNT_EXC'},
                {'code': -310, 'error': 'OP_ERR_MIS_500CNT_EXC'},
                {'code': -340, 'error': 'OP_ERR_WRONG_ACCTINFO'},
                {'code': -500, 'error': 'OP_ERR_ORD_SYMCODE_EMPTY'},
                {'code': -310, 'error': 'OP_ERR_MIS_500CNT_EXC'},
                {'code': -311, 'error': 'OP_ERR_ORD_OVERFLOW'},
                {'code': -340, 'error': 'OP_ERR_ORD_WRONG_ACCTINFO'}
            ])

    """
    Internal print functions
    """
    def print_error(self, function, code):
        error = self.error_dictlist.get_datum(code)
        if error is not None:
            self.log.print('info', '{} failed, error(code:{}/message:{})'.format(function, code, error['error']))
        else:
            self.log.print('info', '{} failed, error(code:{})'.format(function, code))

    def connect_events(self):
        self.OnEventConnect.connect(self._OnEventConnect)
        self.OnReceiveTrData.connect(self._OnReceiveTrData)

        self.event_wait_on_event_connect = PyQt5.QtCore.QEventLoop()
        self.event_wait_on_receive_tr_data = PyQt5.QtCore.QEventLoop()

    """
    Internal waiting functions for the limitation of TR request
    Waiting type for the limitation of TR request : 1 (minimum time gap) or 2 (limitation number)
    """
    # 1 (minimum time gap) : For 1 hour, 1000 times are the limitation of the TR request.
    # 3600 seconds / 1000 times = 3.6 per second
    minimum_time_gap_for_tr_request = 3.6
    last_tr_request_time = datetime.datetime.now()

    def wait_minimum_time_gap_for_tr_request(self):
        time_gap = datetime.datetime.now() - self.last_tr_request_time

        if time_gap.total_seconds() < self.minimum_time_gap_for_tr_request:
            wait_time = self.minimum_time_gap_for_tr_request - time_gap.total_seconds()
            self.log.print('debug', 'Wait for tr request (sec:{})'.format(wait_time))
            time.sleep(wait_time)

        self.last_tr_request_time = datetime.datetime.now()

    # 2 (limitation number)
    # 5 times per 1 second, 100 times per 1 minute, 300 times per 5 minutes, 1000 times per 1 hours
    limitations_for_tr_request = [
        {'time': 1, 'count': 5, 'requests': list()},
        {'time': 60, 'count': 100, 'requests': list()},
        {'time': 300, 'count': 300, 'requests': list()},
        {'time': 3600, 'count': 1000, 'requests': list()}
    ]

    def wait_limitations_for_tr_request(self):
        for limitation in self.limitations_for_tr_request:
            current_time = datetime.datetime.now()

            over_time_count = 0
            for request in limitation['requests']:
                if (current_time - request).total_seconds() > limitation['second']:
                    over_time_count = over_time_count + 1

            while over_time_count:
                limitation['requests'].pop(0)
                over_time_count = over_time_count - 1

            if len(limitation['requests']) == limitation['count']:
                wait_time = limitation['time'] - (current_time - limitation['time'][0]).total_seconds()

                self.log.print(
                    'debug' if wait_time < 3 else 'info', 'Wait(sec:{}) for limit count({}) in sec({})'.format(
                        wait_time, limitation['count'], limitation['time']))

                time.sleep(wait_time)
                limitation['requests'].pop(0)

            limitation['requests'].append(current_time)

    """
    Kiwoom API functions

    The kiwoom API is called though dynamicCall.

    Several functions are needed to be waited to get the result.
    ex. CommConnect, CommRqData
    To wait the result, QEventLoop is used.
    It is the simple sequence.
        > Calling Kiwoom API though dynamicCall
        > Waiting event loop (Thread waits)
        > Event function called by Kiwoom API
        > The event function works to process the result and release the event loop
        > The waiting thread is released
    """

    """
    Calling Kiwoom API methods
    """
    def CommConnect(self):
        result = self.dynamicCall('CommConnect()')
        if 0 == result:
            self.log.print('debug', 'CommConnect() executed and waits OnEventConnect()')
            self.event_wait_on_event_connect.exec_()
        else:
            self.print_error('CommConnect()', result)

        return result

    def CommRqData(self, separator, code, chain, screen):
        self.tr_is_chain_data = False
        self.tr_internal_data = list()

        if tr_request_waiting_type == 1:
            self.wait_minimum_time_gap_for_tr_request()
        elif tr_request_waiting_type == 2:
            self.wait_limitations_for_tr_request()

        result = self.dynamicCall('CommRqData(QString, QString, int, QString)', separator, code, chain, screen)
        if 0 == result:
            self.log.print('debug', 'CommRqData() executed and waits OnReceiveTrData()')
            self.event_wait_on_receive_tr_data.exec_()
        else:
            self.print_error('CommRqData()', result)

        return result, self.tr_is_chain_data, self.tr_internal_data

    def GetLoginInfo(self, tag):
        return self.dynamicCall('GetLoginInfo(QString)', tag)

    def SendOrder(self, separator, screen, account, order_type, code, amount, price, deal_type, order_number):
        result = self.dynamicCall(
            'SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)',
            [separator, screen, account, order_type, code, amount, price, deal_type, order_number])

        if 0 == result:
            self.log.print('debug', 'SendOrder() executed and waits OnReceiveTrData()')
            self.event_wait_on_receive_tr_data.exec_()
        else:
            self.print_error('SendOrder()', result)

        return result

    # SendOrderCredit

    def SetInputValue(self, item, value):
        self.dynamicCall('SetInputValue(QString, QString)', item, value)

    # DisconnectRealData

    def GetRepeatCnt(self, code, recode):
        return self.dynamicCall('GetRepeatCnt(QString, QString)', code, recode)

    # CommKwRqData
    # GetAPIModulePath

    def GetCodeListByMarket(self, market):
        return self.dynamicCall('GetCodeListByMarket(QString)', [market]).strip()

    def GetConnectState(self):
        return self.dynamicCall('GetConnectState()')

    def GetMasterCodeName(self, code):
        return self.dynamicCall('GetMasterCodeName(QString)', [code]).strip()

    # GetMasterListedStockCnt
    # GetMasterConstruction
    # GetMasterListedStockDate
    # GetMasterLastPrice
    # GetMasterStockState
    # GetDataCount
    # GetOutputValue

    def GetCommData(self, code, recode, index, item):
        return self.dynamicCall('GetCommData(QString, QString, int, QString)', code, recode, index, item).strip()

    # GetCommRealData
    # GetChejanData

    def GetThemeGroupList(self, order):
        return self.dynamicCall('GetThemeGroupList(int)', order).strip()

    def GetThemeGroupCode(self, code):
        return self.dynamicCall('GetThemeGroupCode(QString)', code).strip()

    # GetFutureList
    # GetFutureCodeByIndex
    # GetActPriceList
    # GetMonthList
    # GetOptionCode
    # GetOptionCodeByMonth
    # GetOptionCodeByActPrice
    # GetSFutureList
    # GetSFutureCodeByIndex
    # GetSActPriceList
    # GetSMonthList
    # GetSOptionCode
    # GetSOptionCodeByMonth
    # GetSOptionCodeByActPrice
    # GetSFOBasisAssetList
    # GetOptionATM
    # GetSOptionATM
    # GetBranchCodeName
    # SetInfoData
    # SetRealReg
    # SetRealRemove
    # GetConditionLoad
    # GetConditionNameList
    # SendCondition
    # SendConditionStop
    # GetCommDataEx

    """
    Methods what is called by Kiwoom API
    """
    def _OnReceiveTrData(
            self, screen, separator, code, recode, chain, none_used_1, none_used_2, none_used_3, none_used_4):
        self.log.print(
            'debug', 'OnReceiveTrData(screen:{}/separator:{}/code:{}/recode:{}/chain:{}) is called'.format(
                screen, separator, code, recode, chain))

        tran = self.tran_dictlist.get_datum(code)
        if tran is None:
            self.log.print('critical', 'OnReceiveTrData(), code({}) is not supported'.format(code))
            raise AssertionError('OnReceiveTrData(), code({}) is not supported'.format(code))

        if 'data' == tran['type']:
            if '2' == chain:
                self.tr_is_chain_data = True

            data_count = 0
            if tran['data_type'] == 'single':
                data_count = 1
            elif tran['data_type'] == 'multi':
                data_count = self.get_repeat_cnt(code, recode)

            for index in range(data_count):
                datum = dict()

                for result in tran['results']:
                    value = self.GetCommData(code, recode, index, result[0])

                    if len(value) == 0 and (result[2] == 'float' or result[2] == 'int'):
                        value = '0'

                    if result[2] == 'datetime':
                        if result[0] == '일자':
                            datum[result[1]] = datetime.strptime(value, '%Y%m%d')

                        elif result[0] == '체결시간':
                            datum[result[1]] = datetime.strptime(value[:12], '%Y%m%d%H%M')

                        else:
                            self.log.print(
                                'critical', 'TR data({}) is invalid for ({}/{}/{})'.format(
                                    value, result[0], result[1], result[2]))
                            raise AssertionError(
                                'TR data({}) is invalid for ({}/{}/{})'.format(value, result[0], result[1], result[2]))

                    elif result[2] == 'str':
                        datum[result[1]] = value

                    elif result[2] == 'float':
                        if value[0] == '-' or value[0] == '+':
                            value = value[1:]

                        datum[result[1]] = float(value)

                    elif result[2] == 'int':
                        if value[0] == '-' or value[1] == '+':
                            value = value[1:]

                        datum[result[1]] = int(value)

                    else:
                        self.log.print(
                            'critical', 'TR data({}) is invalid for ({}/{}/{})'.format(
                                value, result[0], result[1], result[2]))
                        raise AssertionError(
                            'TR data({}) is invalid for ({}/{}/{})'.format(value, result[0], result[1], result[2]))

                self.tran_dictlist.append(datum)

            self.event_wait_on_receive_tr_data.exit()

    # OnReceiveRealData
    # OnReceiveMsg
    # OnReceiveChejanData

    def _OnEventConnect(self, result):
        if 0 == result:
            self.log.print('debug', 'OnEventConnect({}) is called'.format(result))
        else:
            self.print_error('OnEventConnect({})'.format(result), result)

        self.event_wait_on_event_connect.exit()

    # OnReceiveCondition
    # OnReceiveTrCondition
    # OnReceiveConditionVer
