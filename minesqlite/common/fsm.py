# coding=utf-8
# Author: @hsiaoxychen
"""A simple implementation of FSM (Finite State Machine)."""
import typing
from dataclasses import dataclass


__all__ = ['FiniteStateMachine', 'Transition']


State = typing.TypeVar('State')


@dataclass
class Transition(object):
    trigger: str
    source: State
    dest: State
    side_effects: typing.Optional[list[str]] = None

    def validate(self, states: list[State]):
        assert self.source in states and self.dest in states


class FiniteStateMachine(object):
    def __init__(self,
                 states: list[State],
                 transitions: list[Transition],
                 initial: typing.Optional[State] = None):
        assert len(states) > 1, "at least one state must be provided"
        if initial is None:
            initial = states[0]

        for trans in transitions:
            trans.validate(states)

        self.states: list[State] = states
        self._state: State = initial
        self.transitions: dict[str, list[Transition]] = {}

        for trans in transitions:
            trigger_name = trans.trigger
            self.transitions.setdefault(trigger_name, []).append(trans)

            # closure
            def get_lambda(name):
                return lambda *args, **kwargs: \
                    self._transit(name, *args, **kwargs)

            setattr(self, trigger_name, get_lambda(trigger_name))

    @property
    def state(self):
        return self._state

    def before_change_state(self, from_state: State, to_state: State):
        pass

    def after_change_state(self, from_state: State, to_state: State):
        pass

    def _transit(self, trigger_name, *args, **kwargs):
        candidate_transitions = self.transitions[trigger_name]
        for trans in candidate_transitions:
            if trans.source != self._state:
                continue
            self.before_change_state(self._state, trans.dest)
            if trans.side_effects is not None:
                for side_effect in trans.side_effects:
                    getattr(self, side_effect)(*args, **kwargs)
            self._state = trans.dest
            self.after_change_state(self._state, trans.dest)
            return
        else:
            # no matched transition rules, just leave the state unmodified
            self.before_change_state(self._state, self._state)
            self.after_change_state(self._state, self._state)
