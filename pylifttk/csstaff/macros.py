
import itertools as _itertools
import typing as _typing

import six as _six

import pylifttk.csstaff.api as _api
import pylifttk.csstaff.exceptions as _exc
import pylifttk.csstaff.util as _util


ASDICT_STUDENT_KEY = 'netid'
ASDICT_COURSE_KEY = 'registrar_id'


def course(course_name=None, as_dict=False, simple=False):
    # type: (_typing.Optional[str], bool, bool) -> _typing.Union[_typing.List, _typing.Dict]
    """

    :param course_name:
    :param as_dict:
    :param simple:
    :return:
    """

    # Build endpoint
    endpoint = "course/"
    if course_name and _util.validate_course_name(course_name):
        endpoint += course_name

    # Make request
    result = _api.request(endpoint=endpoint)

    # Post-process result
    if simple:
        result = list(map(lambda item: item[ASDICT_COURSE_KEY], result))

    elif as_dict:
        result = dict([
            (item[ASDICT_COURSE_KEY], item)
            for item in result
        ])

    return result


def course_staff(course_name, category=None, flatten=True):
    _util.validate_course_name(course_name)

    result = course(course_name=course_name)

    if "staff" in result:
        staff = result["staff"]
        people = []

        if category:
            # Managers, dropbox, graders, checkers
            if isinstance(category, (str, _six.text_type)):
                category = [category]

            for c in category:

                if c in staff:
                    # concatenate
                    people = people + staff[c]
                else:
                    raise _exc.CourseAPIException(
                        msg="Category '%s' invalid for course '%s'." %
                        (course_name, c))

            # remove duplicates
            people = list(set(people))

        elif flatten:
            # mash all NetIDs and filter for uniqueness
            lists = staff.values()
            people = list(set(_itertools.chain.from_iterable(lists)))

        else:
            return staff

        people.sort()
        return people

    return []


def course_enrollment(course_name, as_dict=False, force_refresh=False):
    """
    Retrieves a list of all students enrolled in the specified course.
    Optionally if `as_dict` is set to `True` then retrieves a dictionary,
    using the NetID as the key.
    """

    _util.validate_course_name(course_name)

    endpoint = "course_enrollment/{}".format(course_name)

    # Make request
    result = _api.request(endpoint=endpoint)

    if as_dict:
        result = dict([
            (item[ASDICT_STUDENT_KEY], item)
            for item in result
        ])

    return result
