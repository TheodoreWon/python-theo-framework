import threading
import queue
import cmd


class System:
    """
    System provides component and interface functionality.
    It makes you to build your system easily.

    System supports a prompt functionality to execute your system.
    Because the interface module works with registered interfaces by components,
    Please use System with Component class.

    Methods:
        register_interface(component, interface, argument_numbers, func)
        execute_interface(component, interface, *arguments)

        register_component(name, constructor)
        startup_components()

        start_admin_prompt()

        Example:
            if __name__ == "__main__":
                system = System()
                # system.register_component('component', Component)
                system.startup_components()
                system.start_admin_prompt()
    """

    interface_dictlist, component_dictlist = None, None
    log = None

    is_admin_prompt_started = False

    def __init__(self):
        from .DictList import DictList
        if self.interface_dictlist is None:
            self.interface_dictlist = DictList()

        if self.component_dictlist is None:
            self.component_dictlist = DictList('name')

    def register_interface(self, component, interface, argument_numbers, func):
        if self.interface_dictlist.get_datum(
                [{'key': 'component', 'value': component}, {'key': 'interface', 'value': interface}]) is not None:
            raise AssertionError('interface(component:{}/interface:{}) is exist.'.format(component, interface))

        self.interface_dictlist.append(
            {'component': component, 'interface': interface, 'argument_numbers': argument_numbers, 'func': func})

    def execute_interface(self, component, interface, *arguments):
        interface = self.interface_dictlist.get_datum(
            [{'key': 'component', 'value': component}, {'key': 'interface', 'value': interface}])

        if interface is not None and len(arguments) in interface['argument_numbers']:
            return interface['func'](*arguments)

        # print('[System] Warning: interface is not exist.')
        # raise AssertionError('[System] interface is not exist.')
        return None

    def register_component(self, name, constructor):
        if self.component_dictlist.get_datum('name', name) is not None:
            raise AssertionError('component({}) is exist.'.format(name))

        self.component_dictlist.append({'name': name, 'constructor': constructor})

    def startup_components(self):
        componets = []
        for component in self.component_dictlist.get_data():
            componets.append(component['name'])
            component['handler'] = component['constructor'](component['name'])

        for component in self.component_dictlist.get_data():
            component['handler'].check_connected(componets)

        for component in self.component_dictlist.get_data():
            component['handler'].initial()

    def start_admin_prompt(self):
        if not self.is_admin_prompt_started:
            system_queue = queue.Queue()
            prompt_queue = queue.Queue()

            prompt = Prompt()
            prompt.set_queue(system_queue, prompt_queue)
            threading.Thread(target=prompt.cmdloop).start()

            while True:
                messages = system_queue.get()
                if len(messages) == 1 and messages[0] == 'exit':
                    # print('[System] exit')
                    break

                elif len(messages) == 1 and messages[0] == 'get_interfaces':
                    prompt_queue.put(self.interface_dictlist.get_data())

                elif len(messages) >= 2:
                    print('[System] execute interface({})'.format(messages))
                    prompt_queue.put(self.execute_interface(messages[0], messages[1], *messages[2:]))

                else:
                    # print('[System] invalid command({})'.format(messages))
                    prompt_queue.put(None)


system = System()


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

        from .DictList import DictList
        if isinstance(result, DictList):
            print('[Prompt] Result : below dictlist')
            result.print()

        elif isinstance(result, list):
            print('[Prompt] Result : list(num:{})'.format(len(result)))

        else:
            print('[Prompt] Result : {}'.format(result))

        return ''

    def do_exit(self, inputs):
        self.system_queue.put(['exit'])
        return True
