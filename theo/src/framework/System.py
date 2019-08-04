import threading
import queue
import cmd
from theo.src.framework.DictList import DictList


class System:
    """
    System provides component and interface functionality.
    It makes you to build your system easy.

    System supports a prompt functionality to execute your system.
    Because the interface module works with registered interfaces by components,
        please use System with Component.

    Methods:
        register_interface(component, command, argument_numbers, func) : registering interface
        execute_interface(component, command, *arguments) : executing interface

        register_component(constructor)
        register_components(constructors)
        components = get_components() : getting the registered components
        startup_components() : creating registered components and calling the initial function of the components

        start_interface_prompt()

    Example:
        from theo.framework import System, Component


        class TheoFriend(Component):
            def initial(self):
                self.log.print('info', 'initial')
                System.register_interface('TheoFriend', 'print_theo_friend', [1], self.print_theo_friend)

            def print_theo_friend(self, name):
                self.log.print('info', 'Theo has a friend, {}'.format(name))


        System.register_component(TheoFriend)
        System.startup_components()

        System.execute_interface('TheoFriend', 'print_theo_friend', 'Grace')
    """

    interface_dictlist = DictList()
    component_dictlist = DictList()

    is_prompt_started = False

    @staticmethod
    def register_interface(component, command, argument_numbers, func):
        try:
            if not System.interface_dictlist.get([{'key': 'component', 'value': component},
                                                  {'key': 'command', 'value': command}]):
                System.interface_dictlist.append(
                    {'component': component, 'command': command, 'argument_numbers': argument_numbers, 'func': func})
        except Exception as error:
            print(f'error: {error} / System.register_interface(component:{component}/{type(component)},',
                  f'command:{command}/{type(command)},')
            print(f'\targument_numbers:{argument_numbers}/{type(argument_numbers)}, func:{func}/{type(func)})')

    @staticmethod
    def execute_interface(component, command, *arguments):
        try:
            interface = System.interface_dictlist.get([
                {'key': 'component', 'value': component},
                {'key': 'command', 'value': command}
            ])

            if interface and len(arguments) in interface['argument_numbers']:
                return interface['func'](*arguments)

            return None
        except Exception as error:
            print(f'error: {error} / System.execute_interface(component:{component}/{type(component)},',
                  f'command:{command}/{type(command)},')
            print(f'\t*arguments:{arguments}/{type(arguments)})')
            return None

    @staticmethod
    def register_component(constructor):
        try:
            if not System.component_dictlist.get('constructor', constructor):
                System.component_dictlist.append({'constructor': constructor, 'handler': None, 'init': False})
        except Exception as error:
            print(f'error: {error} / System.register_component(constructor:{constructor}/{type(constructor)})')

    @staticmethod
    def register_components(constructors):
        try:
            for constructor in constructors:
                if not System.component_dictlist.get('constructor', constructor):
                    System.component_dictlist.append({'constructor': constructor, 'handler': None, 'init': False})
        except Exception as error:
            print(f'error: {error} / System.register_components(constructor:{constructors}/{type(constructors)})')

    @staticmethod
    def get_components():
        try:
            return list(map(lambda component: component['constructor'].__name__, System.component_dictlist.get_list()))
        except Exception as error:
            print(f'error: {error} / System.get_components()')

    @staticmethod
    def startup_components():
        try:
            for component in System.component_dictlist.get_list():
                if not component['handler']:
                    component['handler'] = component['constructor']()

                if not component['init']:
                    component['handler'].initial()
                    component['init'] = True
        except Exception as error:
            print(f'error: {error} / System.get_components()')

    @staticmethod
    def start_interface_prompt():
        try:
            if not System.is_prompt_started:
                system_queue = queue.Queue()
                prompt_queue = queue.Queue()

                prompt = Prompt()
                prompt.set_queue(system_queue, prompt_queue)
                threading.Thread(target=prompt.cmdloop).start()

                System.is_prompt_started = True

                while True:
                    messages = system_queue.get()
                    if len(messages) == 1 and messages[0] == 'exit':
                        break
                    elif len(messages) == 1 and messages[0] == 'get_interfaces':
                        prompt_queue.put(System.interface_dictlist.get_list())
                    elif len(messages) >= 2:
                        prompt_queue.put(System.execute_interface(messages[0], messages[1], *messages[2:]))
                    else:
                        prompt_queue.put(None)
        except Exception as error:
            print(f'error: {error} / System.start_interface_prompt()')


class Prompt(cmd.Cmd):
    intro = 'help : print user commands what are registered' \
            + '\nexit : quit the prompt'
    prompt = '(prompt) '

    system_queue = None
    prompt_queue = None

    def set_queue(self, system_queue, prompt_queue):
        self.system_queue = system_queue
        self.prompt_queue = prompt_queue

    def precmd(self, inputs):
        try:
            inputs = inputs.split()
            if len(inputs) < 1:
                return ''
            elif len(inputs) == 1 and inputs[0] == 'exit':
                return 'exit'
            elif len(inputs) == 1 and inputs[0] == 'help':
                self.system_queue.put(['get_interfaces'])

                interfaces = self.prompt_queue.get()
                print(f'Interface list(num:{len(interfaces)})')
                for interface in interfaces:
                    print('- {} {} {}'.format(
                        interface['component'], interface['command'], interface['argument_numbers']))

                return ''
            elif len(inputs) < 2:
                print('Invalid command')
                return ''

            self.system_queue.put(inputs)
            result = self.prompt_queue.get()

            if isinstance(result, DictList):
                print('Result : below DictList')
                result.print()
            elif isinstance(result, list):
                print(f'Result : List(num:{len(result)})')
                for index, element in enumerate(result):
                    print(f'[index:{index}] {element}')
            else:
                print(f'Result : {result}/{type(result)}')

            return ''
        except Exception as error:
            print(f'error: {error} / Prompt.precmd(inputs:{inputs}/{type(inputs)})')

    def do_exit(self, inputs):
        self.system_queue.put(['exit'])
        return True
