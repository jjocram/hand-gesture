from collections import namedtuple
from json import load

Transaction = namedtuple("Transaction", ["from_state", "to_state", "with_what"])


class AutomataManager:
    special_chars = {"A-Z"}

    def __init__(self, path: str):
        with open(path) as json_file:
            automata_dict = load(json_file)

        self.current_state = automata_dict.get("initial_state")
        self.transitions = [Transaction(t.get("from"),
                                        t.get("to"),
                                        t.get("with")) for t in automata_dict.get("transitions")]
        self.states = {extract(state)
                       for state in self.transitions
                       for extract in
                       (lambda transition: transition.get("from"), lambda transition: transition.get("to"))}
        self.alphabet = {transition.with_what for transition in self.transitions} - self.special_chars

    def _get_input(self, specific_input):
        pass

    def consume_input(self, specific_input):
        raise NotImplementedError
