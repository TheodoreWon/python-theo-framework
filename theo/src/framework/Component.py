import abc
from theo.src.framework.Log import Log


class Component(metaclass=abc.ABCMeta):
    """
    Component is a system part.
    In the project, components are initialized by system and communicate using interface functions.

    How to use:
        Copy the example and change the ComponentName
        If the component has a dependency with other components,
            define set_related_components and append related_components at self.related_components.
        Define the function, initial and add calling system.register_interface and initial sequence for it.
        Add System.register_component(ComponentName) at program main.
        When main call system.startup_components(), the component will be initialized.

    Example:
        from theo.framework import Component, System


        class ComponentName(Component):
            # def set_related_components(self):
            #     self.related_components.append('ComponentName')

            def initial(self):
                self.log.print('info', 'initial (related:{})'.format(self.related_components))

                # System.register_interface('ComponentName', 'interface', [0], None)
    """

    def __init__(self):
        self.log = Log(type(self).__name__)

        self.related_components = list()
        self.set_related_components()

    def __name__(self):
        return type(self).__name__

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
