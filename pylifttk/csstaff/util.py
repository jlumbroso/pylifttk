
import pylifttk

import pylifttk.csstaff.exceptions


SECTION_NAME = "csstaff"


config = pylifttk.get_local_config(
    section=SECTION_NAME,
    template={
        SECTION_NAME: {
            "username": str,
            "password": str,
        },
    })


def validate_course_key(course_key, silent=False):
    """
    Validate the course course_key with an elementary heuristic (only contains
    alphanumeric characters, dash and underscore).
    """

    for c in course_key:
        if c.isalnum() or c in "_-":
            continue

        if silent:
            return False
        else:
            raise pylifttk.csstaff.exceptions.CourseAPIException(
                msg="Course key '{}' could be malformed.".format(course_key)
            )

    return True


def validate_student_id(name, silent=False):
    """
    Validate the student's ID with an elementary heuristic (only contains
    alphanumeric characters or a dot).
    """

    for c in name:
        if c.isalnum() or c in ".":
            continue

        if silent:
            return False
        else:
            raise pylifttk.csstaff.exceptions.CourseAPIException(
                msg="NetID '{}' could be malformed.".format(name)
            )

    return True