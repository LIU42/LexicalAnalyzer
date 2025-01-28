import re
import json


class Symbol:
    def __init__(self, type, word):
        self.type = type
        self.word = word

    def __len__(self):
        return len(self.word)

    @property
    def is_token(self):
        return self.type != 'spaces'

    @staticmethod
    def operators(word):
        return Symbol('operators', word)

    @staticmethod
    def bounds(word):
        return Symbol('bounds', word)

    @staticmethod
    def spaces(word):
        return Symbol('spaces', word)

    def to_token(self, location):
        lines = location[0]
        index = location[1]

        return Token(lines, index, self.type, self.word)


class Token:
    def __init__(self, lines, index, type, word):
        self.type = type
        self.word = word
        self.lines = lines
        self.index = index

    def __str__(self):
        return f'<{self.lines}, {self.index}, {self.type}, {self.word}>'

    @staticmethod
    def default(location, type, word):
        lines = location[0]
        index = location[1]
        return Token(lines, index, type, word)


class Error:
    def __init__(self, lines, index, message):
        self.lines = lines
        self.index = index
        self.message = message

    def __str__(self):
        return f'Error at lines: {self.lines} column: {self.index} {self.message}'

    @staticmethod
    def unexpected(location):
        lines = location[0]
        index = location[1]
        return Error(lines, index, 'unexpected symbols')

    @staticmethod
    def invalid(location, type):
        lines = location[0]
        index = location[1]
        return Error(lines, index, f'invalid {type}')


class StateTransform:
    def __init__(self, source, symbol, target):
        self.source = source
        self.symbol = symbol
        self.target = target

    def __str__(self):
        return f'({self.source}, {self.symbol}, {self.target})'


class AutomatonGrammar:
    def __init__(self, formulas, alias, start, final):
        self.alias = alias
        self.start = start
        self.final = final
        self.formulas = formulas

    def extract_state_transforms(self):
        for formula in self.formulas:
            if match := re.match(r'(.+?) -> `(.+?)` (.+)', formula):
                source = match.group(1)
                symbol = match.group(2)
                target = match.group(3)

                for symbol in self.alias[symbol]:
                    yield StateTransform(source, symbol, target)

            elif match := re.match(r'(.+?) -> `(.+?)`', formula):
                source = match.group(1)
                symbol = match.group(2)

                for symbol in self.alias[symbol]:
                    yield StateTransform(source, symbol, self.final)

            elif match := re.match(r'(.+?) -> (.) (.+)', formula):
                source = match.group(1)
                symbol = match.group(2)
                target = match.group(3)

                yield StateTransform(source, symbol, target)

            elif match := re.match(r'(.+?) -> (.)', formula):
                source = match.group(1)
                symbol = match.group(2)

                yield StateTransform(source, symbol, self.final)


class SymbolGrammar:
    def __init__(self, keywords, operators, bounds, spaces, constants_specials):
        self.keywords = keywords
        self.operators = operators
        self.bounds = bounds
        self.spaces = spaces
        self.constants_specials = constants_specials


def load_grammar_configs():
    with open('configs/grammar.json', 'r', encoding='utf-8') as grammars:
        return json.load(grammars)


grammar_configs = load_grammar_configs()

constants_grammar = AutomatonGrammar(
    grammar_configs['constants']['formulas'],
    grammar_configs['alias'],
    grammar_configs['identifiers']['start'],
    grammar_configs['identifiers']['final'],
)

identifiers_grammar = AutomatonGrammar(
    grammar_configs['identifiers']['formulas'],
    grammar_configs['alias'],
    grammar_configs['identifiers']['start'],
    grammar_configs['identifiers']['final'],
)

symbols_grammar = SymbolGrammar(
    grammar_configs['keywords'],
    grammar_configs['operators'],
    grammar_configs['bounds'],
    grammar_configs['spaces'],
    grammar_configs['constants']['specials'],
)


def load_constants():
    return constants_grammar


def load_identifiers():
    return identifiers_grammar


def load_symbols():
    return symbols_grammar
