# coding=utf-8
# Author: @hsiaoxychen 2022/06/04
import collections
import enum
import typing


class _State(enum.Enum):
    INITIAL = 'initial'
    IN_RAW_STRING = 'in_raw_string'
    IN_QUOTED_STRING = 'in_quoted_string'


StateTransition = collections.namedtuple('state_transition',
                                         ['next_state', 'extra_step'])

_Else = '_Else'

# INITIAL         ( )     -> INITIAL
# INITIAL         (")     -> IN_QUOTED_STR
# INITIAL         else    -> IN_RAW_STR       [append-buff]
# IN_RAW_STR      ( )     -> INITIAL          [save-buff]
# IN_RAW_STR      else    -> IN_RAW_STR       [append-buff]
# IN_QUOTED_STR   (")     -> INITIAL          [save-buff]
# IN_QUOTED_STR   else    -> IN_QUOTED_STR    [append-buff]
TRANSITIONS = {
    _State.INITIAL: {
        ' ': StateTransition(_State.INITIAL, None),
        '"': StateTransition(_State.IN_QUOTED_STRING, None),
        _Else: StateTransition(_State.IN_RAW_STRING, 'append-buff'),
    },
    _State.IN_RAW_STRING: {
        ' ': StateTransition(_State.INITIAL, 'save-buff'),
        _Else: StateTransition(_State.IN_RAW_STRING, 'append-buff'),
    },
    _State.IN_QUOTED_STRING: {
        '"': StateTransition(_State.INITIAL, 'save-buff'),
        _Else: StateTransition(_State.IN_QUOTED_STRING, 'append-buff'),
    }
}


def split(line) -> typing.List[str]:
    """Split statement into words with proper handling of quotes."""
    results = []
    buff = []
    state = _State.INITIAL

    for ch in line:
        else_trans = TRANSITIONS[state][_Else]
        trans = TRANSITIONS[state].get(ch, else_trans)
        state = trans.next_state
        if trans.extra_step is not None:
            if trans.extra_step == 'append-buff':
                buff.append(ch)
            elif trans.extra_step == 'save-buff':
                results.append(''.join(buff))
                buff.clear()
            else:
                raise ValueError(
                    "Invalid `extra_step` {}".format(trans.extra_step))

    return results
