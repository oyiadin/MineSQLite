# coding=utf-8
# Author: @hsiaoxychen 2022/06/04
"""Split the statement into words with proper handling of quotes.

The process of splitting is implemented as an FSM (finite state machine).
"""
import enum
import typing

from minesqlite.common.fsm import FiniteStateMachine, Transition


class State(enum.Enum):
    """The states of our FSM."""
    # the initial state
    INITIAL = 'initial'
    # the state when inside a raw string (ends with a space)
    IN_RAW_STRING = 'in_raw_string'
    # the state when inside a quoted string (begins and ends with a quote)
    IN_QUOTED_STRING = 'in_quoted_string'


class SplitFSM(FiniteStateMachine):
    """The FSM to iterate over a statement, and splitting it into words.

    STATE describe what situation of the FSM at some point.
    STATES are the full list of possible states.
    TRANSITIONS are rules that, from an original state, what next state we can
        jump to, when we meet specific events (triggers).
    TRIGGER means event, which drives our FSM to traverse among states.

    In this SplitFSM, we have three triggers in total:
    * meet_space: triggered when we meet with a space
    * meet_quote: triggered when we meet with a quote
    * meet_others: triggered when we meet with anything else
    """
    STATES = list(State)
    TRANSITIONS = [
        # we're currently at initial state, and we are dealing with another
        # extra space right now, just ignore it, and stay inside initial state
        Transition(trigger='meet_space',
                   source=State.INITIAL, dest=State.INITIAL,
                   side_effects=['save_next_pos']),
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
                   side_effects=['save_contents_between_pos',
                                 'save_next_pos']),
        # otherwise, just eats in the character

        # quote stops a quoted string
        Transition(trigger='meet_quote',
                   source=State.IN_QUOTED_STRING, dest=State.INITIAL,
                   side_effects=['save_contents_between_pos',
                                 'save_next_pos']),
        # otherwise, just eats in the character
    ]

    def __init__(self, statement: str, *args, **kwargs):
        super().__init__(self.STATES, self.TRANSITIONS, *args, **kwargs)

        self.statement = statement
        self.saved_pos = 0
        self.current_pos = 0
        self.result_words = []

    # some side_effect functions, to be called when traverse among states
    def save_next_pos(self):
        """[SIDE EFFECT] Save the next position (for later use)"""
        self.saved_pos = self.current_pos + 1

    def save_contents_between_pos(self):
        """[SIDE EFFECT] Slice down a word from the original statement.

        From the saved position, to current position (without)"""
        sliced_down = self.statement[self.saved_pos:self.current_pos]
        self.result_words.append(sliced_down)

    # will be called after every state-switching process
    def after_change_state(self, from_state: str, to_state: str):
        """Increment the position variable."""
        self.current_pos += 1


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
