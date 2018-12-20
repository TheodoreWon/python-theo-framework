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
        register_interface(component, interface, argument_numbers, func) : registering interface
        execute_interface(component, interface, *arguments) : executing interface

        register_component(name, constructor)
        startup_components()

        start_prompt()

    Examples:
        from theo.framework import System

        def set_theo_friend(name):
            print('Theo has a friend, {}'.format(name))

        System.register_interface('theo', 'set_theo_friend', [1], set_theo_friend)
        System.execute_interface('theo', 'set_theo_friend', 'Grace')
    """

    interface_dictlist = DictList()
    component_dictlist = DictList('name')

    is_prompt_started = False

    @staticmethod
    def register_interface(component, interface, argument_numbers, func):
        if System.interface_dictlist.get_datum(
                [{'key': 'component', 'value': component}, {'key': 'interface', 'value': interface}]) is None:
            System.interface_dictlist.append(
                {'component': component, 'interface': interface, 'argument_numbers': argument_numbers, 'func': func})
        else:
            print('[theo.framework.System] warning: interface(component:{}/interface:{}) is already registered.'.format(
                component, interface))

    @staticmethod
    def execute_interface(component, interface, *arguments):
        interface = System.interface_dictlist.get_datum(
            [{'key': 'component', 'value': component}, {'key': 'interface', 'value': interface}])

        if interface is not None and len(arguments) in interface['argument_numbers']:
            return interface['func'](*arguments)

        print('[theo.framework.System] warning: interface(component:{}/interface:{}) is not exist.'.format(
            component, interface))
        return None

    @staticmethod
    def register_component(name, constructor):
        if System.component_dictlist.get_datum('name', name) is None:
            System.component_dictlist.append({'name': name, 'constructor': constructor,
                                              'handler': None, 'init': False})
        else:
            print('[theo.framework.System] warning: component({}) is already registered.')

    @staticmethod
    def startup_components():
        componets = []
        for component in System.component_dictlist.get_data():
            componets.append(component['name'])

            if component['handler'] is None:
                component['handler'] = component['constructor'](component['name'])

        for component in System.component_dictlist.get_data():
            if not component['init']:
                component['handler'].check_connected(componets)
                component['handler'].initial()

                component['init'] = True

    @staticmethod
    def start_prompt():
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
                    # print('[System] exit')
                    break

                elif len(messages) == 1 and messages[0] == 'get_interfaces':
                    prompt_queue.put(System.interface_dictlist.get_data())

                elif len(messages) >= 2:
                    print('[System] execute interface({})'.format(messages))
                    prompt_queue.put(System.execute_interface(messages[0], messages[1], *messages[2:]))

                else:
                    # print('[System] invalid command({})'.format(messages))
                    prompt_queue.put(None)
        else:
            print('[theo.framework.System] warning: prompt is already started.')


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
        if self.system_queue is None:
            raise AssertionError('system_queue is not set.')

        if self.prompt_queue is None:
            raise AssertionError('prompt_queue is not set.')

        inputs = inputs.split()
        if len(inputs) < 1:
            return ''

        elif len(inputs) == 1 and inputs[0] == 'exit':
            return 'exit'

        elif len(inputs) == 1 and inputs[0] == 'help':
            self.system_queue.put(['get_interfaces'])

            interfaces = self.prompt_queue.get()
            print('interface list(num:{})'.format(len(interfaces)))
            for interface in interfaces:
                print('- {} {} {}'.format(
                    interface['component'], interface['interface'], interface['argument_numbers']))

            return ''

        elif len(inputs) < 2:
            print('[Prompt] Invalid command')
            return ''

        self.system_queue.put(inputs)
        result = self.prompt_queue.get()

        if isinstance(result, DictList):
            print('[Prompt] Result : below dictlist')
            result.print()

        elif isinstance(result, list):
            print('[Prompt] Result : list(num:{})'.format(len(result)))
            for index, datum in enumerate(result):
                print('{} {}'.format(index, datum))

        else:
            print('[Prompt] Result : {}'.format(result))

        return ''

    def do_exit(self, inputs):
        self.system_queue.put(['exit'])
        return True
