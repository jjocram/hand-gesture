import sys

from controller.AutomataManager import AutomataManager


class MacroRunner:
    def __init__(self, macro_file_path: str, automata_descriptor_path: str):
        self.state = 'q0'
        self.macro_file_path = macro_file_path
        self.automata = AutomataManager(automata_descriptor_path, execute_actions=True)

    def run(self):
        with open(self.macro_file_path) as macro_file:
            # actions = [item for sub_list in [el.split() for el in macro_file.readlines()] for item in sub_list]

            for line, action in enumerate(macro_file.read().splitlines()):
                input_accepted = self.automata.consume_input(action)
                if not input_accepted:
                    print(f"Macro fiele {self.macro_file_path} contains command {action} at line {line}")
                    sys.exit(1)
