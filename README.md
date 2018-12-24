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
