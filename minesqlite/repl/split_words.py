# coding=utf-8
# Author: @hsiaoxychen 2022/06/04
"""Split the statement into words with proper handling of quotes.

The process of splitting is implemented as an FSM (finite state machine).
"""
import enum
import functools
import typing

from minesqlite.common.fsm import FiniteStateMachine, Transition


class _SplitFSM(FiniteStateMachine):
    def __init__(self, statement: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.statement = statement
        self.saved_pos = 0
        self.current_pos = 0
        self.result_words = []

    def save_next_pos(self):
        self.saved_pos = self.current_pos + 1

    def save_contents_between_pos(self):
        sliced_down = self.statement[self.saved_pos:self.current_pos]
        self.result_words.append(sliced_down)

    def after_change_state(self, from_state: str, to_state: str):
        self.current_pos += 1


class State(enum.Enum):
    """The states of our FSM."""
    INITIAL = 'initial'
    IN_RAW_STRING = 'in_raw_string'
    IN_QUOTED_STRING = 'in_quoted_string'


SplitFSM = functools.partial(
    _SplitFSM,
    states=list(State),
    transitions=[
        # we've met another extra space, just ignore it
        Transition(trigger='meet_space',
                   source=State.INITIAL, dest=State.INITIAL),
        # a quote is the beginning of a quoted-string
        Transition(trigger='meet_quote',
                   source=State.INITIAL, dest=State.IN_QUOTED_STRING,
                   side_effects=['save_next_pos']),
        # otherwise, starts the process of handling raw string
        Transition(trigger='meet_others',
                   source=State.INITIAL, dest=State.IN_RAW_STRING),

        # space stops a raw string
        Transition(trigger='meet_space',
                   source=State.IN_RAW_STRING, dest=State.INITIAL,
                   side_effects=['save_contents_between_pos', 'save_next_pos']),
        # otherwise, just eats in the character

        # quote stops a quoted string
        Transition(trigger='meet_quote',
                   source=State.IN_QUOTED_STRING, dest=State.INITIAL,
                   side_effects=['save_contents_between_pos', 'save_next_pos']),
        # otherwise, just eat in the character
    ]
)


def split_words(line) -> typing.List[str]:
    """Split statement into words with proper handling of quotes."""
    statement = line + ' '  # a trick to correctly handle the last word
    fsm: SplitFSM = SplitFSM(statement)

    for ch in statement:
        if ch == ' ':
            fsm.meet_space()  # noqa
        elif ch == '"':
            fsm.meet_quote()  # noqa
        else:
            fsm.meet_others()  # noqa

    return fsm.result_words
