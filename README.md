# theo-framework

It is the framework what makes building a project easy.

DictList is the data structure to control data easily and efficiently.
Log is made to log a program by printing and storing.
System and Component make building a system easy.

I am likely waiting a any kind of contribution.


# Theo series

Framework : pip install theo-framework, https://github.com/TheodoreWon/python-theo-framework  
Database : pip install theo-database, https://github.com/TheodoreWon/python-theo-database  
Message : pip install theo-message, https://github.com/TheodoreWon/python-theo-message  
Internet : pip install theo-message, https://github.com/TheodoreWon/python-theo-internet  
Trade : pip install theo-trade, https://github.com/TheodoreWon/python-theo-trade


# How to use

Install the framework  
> pip install theo-framework

Print docstrings  
> from theo.framework import DictList, Log, System, Component  
> print(DictList.&#95;&#95;doc&#95;&#95;)  
> print(Log.&#95;&#95;doc&#95;&#95;)  
> print(System.&#95;&#95;doc&#95;&#95;)  
> print(Component.&#95;&#95;doc&#95;&#95;)  

Simple example (For System, Component, please refer docstrings)  
> ''' import theo-framework '''  
> from theo.framework import Log, DictList  

> ''' print log using Log '''  
> Log.configure(print_enabled=True, store_enabled=True) : default of store_enable is False  
> log = Log('main')  
> log.print('info', 'Hello, theo-framework!')  
>> [2018-12-31 13:29:27,958][main][info] Hello, theo-framework! : log file will be stored.  

> ''' print csv file using DictList '''  
> import os  
> kospi_dictlist = DictList('code')  
> kospi_dictlist.import_csv(os.path.join(os.getcwd(), 'kospi.csv'))  
> kospi_dictlist.print()  
>> DictList(num:1523/key:code) walkers(num:0)  
>> 0 {'code': '000020', 'tag': '', '250 days high': '13400.0', '250 days low': '7500.0', 'eps': '1683.0', 'market capitalization': '2623.0', 'net profit': '470.0', 'net sales': '2589.0', 'operating profit': '110.0', 'pbr': '0.88', 'per': '5.58', 'roe': '17.1'}  
>> 1 {'code': '000030', 'tag': 'kospi100/kospi50', '250 days high': '17400.0', '250 days low': '13550.0', 'eps': '2237.0', 'market capitalization': '108160.0', 'net profit': '15301.0', 'net sales': '85507.0', 'operating profit': '21567.0', 'pbr': '0.53', 'per': '7.15', 'roe': '7.4'}  
>> 2 {'code': '000040', 'tag': '', '250 days high': '760.0', '250 days low': '317.0', 'eps': '-263.0', 'market capitalization': '684.0', 'net profit': '-315.0', 'net sales': '417.0', 'operating profit': '-260.0', 'pbr': '1.51', 'per': '0.0', 'roe': '-61.3'}  
>> ...  
>> 1520 {'code': '590017', 'tag': '', '250 days high': '12600.0', '250 days low': '11020.0', 'eps': '0.0', 'market capitalization': '242.0', 'net profit': '0.0', 'net sales': '0.0', 'operating profit': '0.0', 'pbr': '0.0', 'per': '0.0', 'roe': '0.0'}  
>> 1521 {'code': '590018', 'tag': '', '250 days high': '13115.0', '250 days low': '7880.0', 'eps': '0.0', 'market capitalization': '173.0', 'net profit': '0.0', 'net sales': '0.0', 'operating profit': '0.0', 'pbr': '0.0', 'per': '0.0', 'roe': '0.0'}  
>> 1522 {'code': '900140', 'tag': '', '250 days high': '5650.0', '250 days low': '1750.0', 'eps': '311.0', 'market capitalization': '1209.0', 'net profit': '136.0', 'net sales': '3334.0', 'operating profit': '-226.0', 'pbr': '0.27', 'per': '8.11', 'roe': '3.4'}  

> ''' get datum '''  
> print(kospi_dictlist.get_datum('000060'))  
>> {'code': '000060', 'tag': '', '250 days high': '25750.0', '250 days low': '17400.0', 'eps': '3479.0', 'market capitalization': '23532.0', 'net profit': '3846.0', 'net sales': '64287.0', 'operating profit': '5136.0', 'pbr': '1.28', 'per': '5.95', 'roe': '22.5'}  

> ''' get datum '''  
> print(kospi_dictlist.get_datum('roe', '17.1'))  
>> {'code': '000020', 'tag': '', '250 days high': '13400.0', '250 days low': '7500.0', 'eps': '1683.0', 'market capitalization': '2623.0', 'net profit': '470.0', 'net sales': '2589.0', 'operating profit': '110.0', 'pbr': '0.88', 'per': '5.58', 'roe': '17.1'}  

> ''' get data '''  
> print(kospi_dictlist.get_data([{'key': 'net sales', 'value': '0.0'}, {'key': 'net profit', 'value': '0.0'}]))  
>> [{'code': '000075', 'tag': '', '250 days high': '70900.0', '250 days low': '45050.0', 'eps': '0.0', 'market capitalization': '145.0', 'net profit': '0.0', 'net sales': '0.0', 'operating profit': '0.0', 'pbr': '0.0', 'per': '0.0', 'roe': '0.0'}, {'code': '000087', 'tag': '', '250 days high': '19200.0', '250 days low': '13550.0', 'eps': '0.0', 'market capitalization': '163.0', 'net profit': '0.0', 'net sales': '0.0', 'operating profit': '0.0', 'pbr': '0.0', 'per': '0.0', 'roe': '0.0'}, {'code': '000105', 'tag': '', '250 days high': '296000.0', '250 days low': '161000.0', 'eps': '0.0', 'market capitalization': '514.0', 'net profit': '0.0', 'net sales': '0.0', 'operating profit': '0.0', 'pbr': '0.0', 'per': '0.0', 'roe': '0.0'}, {'code': '000145', 'tag': '', '250 days high': '10700.0', '250 days low': '7020.0', 'eps': '0.0', 'market capitalization': '39.0', 'net profit': '0.0', 'net sales': '0.0', 'operating profit': '0.0', 'pbr': '0.0', 'per': '0.0', 'roe': '0.0'}, {'code': '000155', 'tag': '', '250 days high': '84300.0', '250 days low': '69800.0', 'eps': '0.0', 'market capitalization': '3427.0', 'net profit': '0.0', 'net sales': '0.0', 'operating profit': '0.0', 'pbr': '0.0', 'per': '0.0', 'roe': '0.0'}, ...  

> ''' export '''  
>> kospi_dictlist.import_mongodb('kospi', 'codes')  


# Authors

Theodore Won - Owner of this project


# License

This project is licensed under the MIT License - see the LICENSE file for details


# Versioning

Basically, this project follows the 'Semantic Versioning'. (https://semver.org/)  
But, to notify new feature, I added several simple rules at the Semantic Versioning.  
I would like to call 'Theo Versioning'.

- Version format is MAJOR.MINOR.PATCH  
- MAJOR version is increased when API is changed or when new feature is provided.  
  - New feature does not affect a interface.  
  - But, to notify new feature, New feature makes MAJOR version up.  
  - Before official version release (1.0.0), MAJOR is kept 0 and MINOR version is used.  
- MINOR version is up when the API is added. (New functionality)  
- PATCH version is lifted when bug is fixed, test code is uploaded, comment or document or log is updated.  
