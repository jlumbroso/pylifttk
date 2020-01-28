
import collections as _collections
import copy as _copy
import typing as _typing

import pylifttk
import pylifttk.util


DEFAULT_GRADE = "F"

DEFAULT_CUTOFFS = _collections.OrderedDict([
    ('A', 93),
    ('A-', 90),
    ('B+', 87),
    ('B', 83),
    ('B-', 80),
    ('C+', 77),
    ('C', 73),
    ('C-', 70),
    ('D', 60),
    ('F', 0)
])


try:
    _policy = pylifttk.config["policy"].get()
except: # confuse.NotFoundError
    _policy = {}

try:
    _cutoffs = _policy.get("cutoffs", DEFAULT_CUTOFFS)
except: # confuse.NotFoundError
    _cutoffs = DEFAULT_CUTOFFS

_cutoff_intervals = sorted([
        (lower_cutoff, letter)
        for (letter, lower_cutoff) in _cutoffs.items()
    ],
    reverse=False)


def get_letter_from_raw_score(raw_score, cutoffs=None, extend_cutoffs=True):
    cutoffs_intervals = _cutoff_intervals

    if cutoffs is not None:

        # If `extend` is true, then do not expected `cutoffs` to contain
        # all the letters.
        if extend_cutoffs:
            tmp = _copy.deepcopy(DEFAULT_CUTOFFS)
            tmp.update(cutoffs)
            cutoffs = tmp

        cutoff_intervals = sorted([
                (lower_cutoff, letter)
                for (letter, lower_cutoff) in cutoffs.items()
            ],
            reverse=True)

    for (cutoff, letter) in cutoffs_intervals:
        if raw_score >= cutoff:
            return letter

    return DEFAULT_GRADE


def get_totals():
    try:
        return _policy.get("totals")
    except:
        return