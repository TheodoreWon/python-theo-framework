import abc
from theo.src.framework.Log import Log


class Component(metaclass=abc.ABCMeta):
    """
    Component is a system part.
    In the project, components are initialized by system and communicate using interface functions.

    How to use:
        Copy the example and change the ComponentName
        If the component has a dependency with other components,
            class the System.get_components() and check the existence.
        Define the function, initial and add calling system.register_interface and initial sequence for it.
        Add System.register_component(ComponentName) at program main.
        When main call system.startup_components(), the component will be initialized.

    Example:
        Please refer the docstings of System
    """

    def __init__(self):
        self.log = Log(type(self).__name__)

    def __name__(self):
        return type(self).__name__

    @abc.abstractmethod
    def initial(self):
        pass
