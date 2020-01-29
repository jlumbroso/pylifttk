
import collections as _collections
import copy as _copy
import numbers as _numbers
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

###############################################################################
# Parsing the policy configuration
###############################################################################

# Root course policy

try:
    _policy = pylifttk.config["policy"].get()
except: # confuse.NotFoundError
    _policy = {}

# Letter grade cut-offs

try:
    _cutoffs = _policy.get("cutoffs", DEFAULT_CUTOFFS)
except: # confuse.NotFoundError
    _cutoffs = DEFAULT_CUTOFFS

_cutoff_intervals = sorted([
        (lower_cutoff, letter)
        for (letter, lower_cutoff) in _cutoffs.items()
    ],
    reverse=True)

# Graded work totals (FIXME: validate they are all floats)

try:
    _totals = _policy.get("totals")
except: # confuse.NotFoundError
    _totals = dict()

# Weights

try:
    _raw_weights = _policy.get("weights")
except: # confuse.NotFoundError
    _raw_weights = list()

_weights = list()

for weight in _raw_weights:
    # Two types
    # 1. Single work { "Atomic" : 10.0 }
    # 2. Group work
    #    {
    #       "name":   "assignments",
    #       "weight": 15.0,
    #       "content": [
    #           "Programming Exam 1",
    #           "Programming Exam 2"
    #        ]
    #     }

    # not a dict entry
    if not isinstance(weight, _collections.abc.Mapping):
        continue

    # a group work entry
    if "weight" in weight and "content" in weight:
        _weights.append(weight)
        continue

    # a single work entry
    try:
        (work_name, work_weight) = list(weight.items())[0]
    except ValueError:
        continue

    # transform into single group work
    _weights.append({
        "name": work_name,
        "weight": work_weight,
        "content": [ work_name ]
    })

# Lateness policy

try:
    _lateness = _policy.get("lateness")
except: # confuse.NotFoundError
    _lateness = dict()

###############################################################################


def letter_from_raw_score(raw_score, cutoffs=None, extend_cutoffs=True):
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


def totals():
    try:
        return _copy.deepcopy(_totals)
    except:
        return


def weights():
    try:
        return _copy.deepcopy(_totals)
    except:
        return


def raw_score_from_grade_record(
        grade_record,
        ignore_missing_assessment=False,
        skipped_assessments=None,
        count_data_points=True,
):
    raw_score = 0.0
    data_points = 0

    for weight_group in _weights:

        numerator = 0.0
        denominator = 0.0

        for item in weight_group["content"]:

            # Assessment that we did not expect to get

            if item not in _totals:
                raise Exception("assessment {} not found in totals".format(item))

            # Skipped assessment are ignore for:
            #  - numerator (points the student would get)
            #  - denominator (renormalization of the component)

            if skipped_assessments is not None and item in skipped_assessments:
                continue

            # When `ignore_missing_assessment` is True then
            # we ignore assessment that are missing in the renormalization

            if item not in grade_record and ignore_missing_assessment:
                continue

            # Otherwise the assessment affects the denominator

            denominator += _totals.get(item)

            # And if the student did the assessment, the score is counted
            # in the numerator

            if item in grade_record:
                numerator += grade_record.get(item)

                # Count actual data points used in computation
                data_points += 1

        # Once we have summed all the individual assessments in a weight group
        # we can compute the weighted fraction

        weighted_fraction = (
                float(weight_group["weight"]) *
                float(numerator)
        ) / float(denominator)

        raw_score += weighted_fraction

    if count_data_points:
        return raw_score, data_points
    else:
        return raw_score


def compute_late_penalty(netid, late_data=None):
    if late_data is None or netid not in late_data:
        return 0.0

    # Retrieve computed late days
    student_late_record = late_data.get(netid)

    # Try to determine the total
    student_late_day_total = 0.0

    # The record could be a dictionary of lateness per assignment
    if isinstance(student_late_record, _collections.abc.Mapping):
        student_late_day_total = sum(student_late_record.values())

    # Or it could be the computed total of late days
    elif isinstance(student_late_record, _numbers.Number):
        student_late_day_total =  float(student_late_record)

    # Remove allotted days
    student_late_day_total -= pylifttk.policy._lateness.get("allotted", 0)

    # Lower-bound by 0
    student_late_day_total = max(student_late_day_total, 0)

    # Compute a penalty
    student_late_penalty = (
            student_late_day_total *
            pylifttk.policy._lateness.get("penalty", 0.0))

    return student_late_penalty
