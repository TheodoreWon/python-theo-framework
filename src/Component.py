import abc

from .Validation import Validation


class Component(metaclass=abc.ABCMeta):
    """
    Component is a system part.
    In the project, components are initialized and communicated using interface functions.
    Please use System with Component class.

    How to use:
        Copy the example and change the --component-name--
        Define the function, set_related_components and append related_components at self.related_components.
        Define the function, initial and add calling system.register_interface and initial sequence for it.
        Add system.register_component('--component-name--', --component-name--) at program main.
        When program main call system.startup_components(), the component will be initialized.

        You can refer MongoDBCtrl class from comp/MongoDBCtrl.py.

    Example:
        from python-library.src.Component import Component
        from python-library.src.System import system


        class --component--name--(Component):
            def set_related_components(self):
                # self.related_components.append('--component--name--')
                self.related_components.clear()

            def initial(self):
                self.log.print('info', 'initial (related:{})'.format(self.related_components))

                # system.register_interface(self.name, 'interface', [0], None)
    """

    def __init__(self, name):
        Validation.validate_name(name)

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
