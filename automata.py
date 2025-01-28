import collections


class StateTransformGraph:
    def __init__(self, default=None):
        self.start = None
        self.final = None
        self.transforms = collections.defaultdict(lambda: collections.defaultdict(default))
        self.characters = None

    def __getitem__(self, args):
        source = args[0]
        symbol = args[1]
        return self.transforms[source][symbol]

    def __setitem__(self, args, target):
        source = args[0]
        symbol = args[1]
        self.transforms[source][symbol] = target

    def exist(self, source, symbol):
        return symbol in self.transforms[source]

    def all_characters(self):
        if self.characters is None:
            self.characters = {character for transform in self.transforms.values() for character in transform.keys() if character != 'ε'}
        return self.characters

    def closure(self, states):
        states_closure = states.copy()
        new_states = states.copy()

        while len(new_states) > 0:
            searchable_states = new_states.copy()
            new_states.clear()

            for state in searchable_states:
                new_states = new_states.union(self.transforms[state]['ε'].difference(states_closure))

            states_closure = states_closure.union(new_states)

        return frozenset(states_closure)

    def move(self, states, character):
        return {target for state in states for target in self.transforms[state][character]}

    def reachable_states(self, states, character):
        return self.closure(self.move(states, character))


class FiniteAutomaton:
    def __init__(self, name, grammar):
        self.state = None
        self.name = name
        self.state_transform_graph = construct_dfa(grammar)

    @property
    def reached_final(self):
        return self.state in self.state_transform_graph.final

    def reset(self):
        self.state = self.state_transform_graph.start

    def transform(self, character):
        try:
            self.state = self.state_transform_graph[self.state, character]
            return True
        except KeyError:
            return False

    def transformable(self, character):
        return self.state_transform_graph.exist(self.state, character)


def construct_nfa(grammar):
    nfa_transform_graph = StateTransformGraph(set)

    for transform in grammar.extract_state_transforms():
        source = transform.source
        symbol = transform.symbol
        target = transform.target

        nfa_transform_graph.transforms[source][symbol].add(target)

    nfa_transform_graph.start = grammar.start
    nfa_transform_graph.final = grammar.final

    return nfa_transform_graph


def find_numbers(number_allocation, state):
    return {number for states, number in number_allocation.items() if state in states}


def ensure(nfa_transform_graph):
    start_states = nfa_transform_graph.closure({nfa_transform_graph.start})

    number_allocation = {start_states: 0}
    new_states_set = {start_states}

    dfa_transform_graph = StateTransformGraph()

    while len(new_states_set) > 0:
        searchable_states_set = new_states_set.copy()
        new_states_set.clear()

        for states in searchable_states_set:
            for character in nfa_transform_graph.all_characters():
                target_states = nfa_transform_graph.reachable_states(states, character)

                if len(target_states) == 0:
                    continue
                if target_states not in number_allocation:
                    new_states_set.add(target_states)
                    number_allocation[target_states] = len(number_allocation)

                dfa_transform_graph[number_allocation[states], character] = number_allocation[target_states]

    dfa_transform_graph.final = find_numbers(number_allocation, nfa_transform_graph.final)
    dfa_transform_graph.start = find_numbers(number_allocation, nfa_transform_graph.start).pop()

    return dfa_transform_graph


def construct_dfa(grammar):
    return ensure(construct_nfa(grammar))
