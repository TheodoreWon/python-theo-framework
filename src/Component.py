import abc


class Component(metaclass=abc.ABCMeta):
    """
    Component is a system part.
    In the project, components are initialized and communicated using interface functions.
    Please use System with Component class.

    At the last of this file, there is the form for initial component.
    """

    def __init__(self, name):
        if not isinstance(name, str):
            raise AssertionError('name(type:{}) should be str.'.format(type(name)))

        self.name = name

        from .Log import Log
        self.log = Log(self.name)

        self.related_components = []
        self.set_related_components()

    @abc.abstractmethod
    def set_related_components(self):
        pass

    def check_connected(self, components):
        for component in self.related_components:
            if component not in components:
                self.log.print('critical', 'component({}) is not connected.'.format(component))
                raise AssertionError('component({}) is not connected.'.format(component))

    @abc.abstractmethod
    def initial(self):
        pass


'''
from theoLibrary.src.Component import Component
from theoLibrary.src.System import system


class --component--(Component):
    def set_related_components(self):
        # self.related_components.append('--component--')
        self.related_components.clear()

    def initial(self):
        self.log.print('info', 'initial (related:{})'.format(self.related_components))

        # system.register_interface(self.name, 'interface', [0], None)
'''
