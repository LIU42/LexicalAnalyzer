import grammars

from grammars import Token
from grammars import Error
from grammars import Symbol

from automata import FiniteAutomaton


constants_automaton = FiniteAutomaton('constants', grammars.load_constants())
constants_automaton.reset()

identifiers_automaton = FiniteAutomaton('identifiers', grammars.load_identifiers())
identifiers_automaton.reset()

symbols = grammars.load_symbols()


def allocate_automaton(character):
    if constants_automaton.transformable(character):
        return constants_automaton
    if identifiers_automaton.transformable(character):
        return identifiers_automaton


class LexicalAnalyzer:
    def __init__(self):
        self.automaton = None
        self.lines = 0
        self.index = 0
        self.contents = ''
        self.token = ''
        self.tokens = []
        self.errors = []

    @property
    def reached_end(self):
        return self.index >= len(self.contents)

    @property
    def token_location(self):
        return self.lines, self.index - len(self.token)

    @property
    def pending_character(self):
        return self.contents[self.index]

    @property
    def pending_contents(self):
        return self.contents[self.index:]

    @property
    def token_valid(self):
        return self.automaton.name != 'constants' or self.match_symbols()

    def transform_success(self):
        transform_success = self.automaton.transform(self.pending_character)

        if transform_success:
            self.token += self.pending_character
            self.index += 1

        return transform_success

    def release_automaton(self):
        self.token = ''
        self.automaton.reset()
        self.automaton = None

    def match(self, symbols):
        for symbol in filter(self.pending_contents.startswith, symbols):
            return symbol

    def match_symbols(self):
        if symbol := self.match(symbols.bounds):
            return Symbol.bounds(symbol)

        if symbol := self.match(symbols.spaces):
            return Symbol.spaces(symbol)

        if symbol := self.match(symbols.operators):
            return Symbol.operators(symbol)

    def analysis_symbols(self):
        symbol = self.match_symbols()

        if symbol is None:
            self.errors.append(Error.unexpected(self.token_location))
            self.index += 1
        else:
            if symbol.is_token:
                self.tokens.append(symbol.to_token(self.token_location))
            self.index += len(symbol)

    def type_recheck(self):
        if self.automaton.name == 'identifiers':
            if self.token in symbols.keywords:
                return 'keywords'
            if self.token in symbols.constants_specials:
                return 'constants'
        return self.automaton.name

    def analysis_variables(self):
        if self.automaton.reached_final and self.token_valid:
            self.tokens.append(Token.default(self.token_location, self.type_recheck(), self.token))
        else:
            self.errors.append(Error.invalid(self.token_location, self.automaton.name))

        self.release_automaton()

    def analysis_contents(self):
        self.index = 0
        self.token = ''
        self.automaton = None

        while not self.reached_end:
            if self.automaton is None:
                self.automaton = allocate_automaton(self.pending_character)

            if self.automaton is None:
                self.analysis_symbols()

            elif not self.transform_success():
                self.analysis_variables()

    def analysis(self, inputs):
        self.tokens.clear()
        self.errors.clear()

        for lines, contents in enumerate(inputs, start=1):
            self.lines = lines
            self.contents = contents
            self.analysis_contents()

        return self.tokens, self.errors
