
import itertools as _itertools
import typing as _typing

import six as _six

import pylifttk.csstaff.api
import pylifttk.csstaff.exceptions
import pylifttk.csstaff.util


ASDICT_STUDENT_KEY = 'netid'
ASDICT_COURSE_KEY = 'registrar_id'


def course(course_key=None, as_dict=False, simple=False):
    # type: (_typing.Optional[str], bool, bool) -> _typing.Union[_typing.List, _typing.Dict]
    """

    :param course_key:
    :param as_dict:
    :param simple:
    :return:
    """

    # Build endpoint
    endpoint = "course/"
    if course_key and pylifttk.csstaff.util.validate_course_key(course_key):
        endpoint += course_key

    # Make request
    result = pylifttk.csstaff.api.request(endpoint=endpoint)

    # Post-process result
    if simple:
        result = list(map(lambda item: item[ASDICT_COURSE_KEY], result))

    elif as_dict:
        result = dict([
            (item[ASDICT_COURSE_KEY], item)
            for item in result
        ])

    return result


def course_staff(course_key, category=None, flatten=True):
    pylifttk.csstaff.util.validate_course_key(course_key)

    result = course(course_key=course_key)

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
                    raise pylifttk.csstaff.exceptions.CourseAPIException(
                        msg="Category '%s' invalid for course '%s'." %
                        (course_key, c))

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


def course_enrollment(course_key, as_dict=False, force_refresh=False):
    """
    Retrieves a list of all students enrolled in the specified course.
    Optionally if `as_dict` is set to `True` then retrieves a dictionary,
    using the NetID as the key.
    """

    pylifttk.csstaff.util.validate_course_key(course_key)

    endpoint = "course_enrollment/{}".format(course_key)

    # Make request
    result = pylifttk.csstaff.api.request(endpoint=endpoint)

    if as_dict:
        result = dict([
            (item[ASDICT_STUDENT_KEY], item)
            for item in result
        ])

    return result
