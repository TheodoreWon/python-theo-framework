import abc

from .System import System
from .Log import Log


class Component(metaclass=abc.ABCMeta):
    """
    Component is a system part.
    In the project, components are initialized and communicated using interface functions.
    Please use System with Component class.

    At the last of this file, there is the form for initial component.
    """

    def __init__(self, system, name):
        if not isinstance(system, System):
            raise AssertionError('system(type:{}) should be System.'.format(type(system)))

        if not isinstance(name, str):
            raise AssertionError('name(type:{}) should be str.'.format(type(name)))

        self.system = system
        self.name = name

        self.related_components = []
        self.log = Log(self.name)
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
from library.src.Component import Component


class --component--(Component):
    def set_related_components(self):
        # self.related_components.append('--component--')
        self.related_components.clear()

    def initial(self):
        self.log.print('info', 'initial (related:{})'.format(self.related_components))

        # self.system.register_interface(self.name, 'interface', [0], None)
'''
