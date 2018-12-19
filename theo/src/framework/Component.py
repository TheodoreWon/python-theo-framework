import abc
from theo.src.framework.Log import Log
from theo.src.framework.System import System


class Component(metaclass=abc.ABCMeta):
    """
    Component is a system part.
    In the project, components are initialized and communicated using interface functions.
    Please use System with Component class.

    How to use:
        Copy the example and change the ComponentName
        Define the function, set_related_components and append related_components at self.related_components.
        Define the function, initial and add calling system.register_interface and initial sequence for it.
        Add system.register_component('ComponentName', ComponentName) at program main.
        When program main call system.startup_components(), the component will be initialized.

    Example:
        from theo.framework import Component


        class ComponentName(Component):
            def set_related_components(self):
                self.related_components.append('ComponentName')

            def initial(self):
                self.log.print('info', 'initial (related:{})'.format(self.related_components))

                self.system.register_interface(self.name, 'interface', [0], None)
    """

    def __init__(self, name, system):
        if not isinstance(name, str):
            raise AssertionError('name(type:{}) should be str.'.format(type(name)))

        if not isinstance(system, System):
            raise AssertionError('system(type:{}) should be theo.framework.System.'.format(type(system)))

        self.name = name
        self.system = system
        self.log = Log(self.name)

        self.related_components = list()
        self.set_related_components()

    def set_related_components(self):
        self.related_components.clear()

    def check_connected(self, registered_components):
        not_connected_component = list()
        for component in self.related_components:
            if component not in registered_components:
                not_connected_component.append(component)
                self.log.print(
                    'critical', '[theo.framework.Component] warning: component({}) is not connected.'.format(component))

        for component in not_connected_component:
            self.related_components.remove(component)

    @abc.abstractmethod
    def initial(self):
        pass
