
import pylifttk

import pylifttk.csstaff.exceptions


SECTION_NAME = "tigerfile"


config = pylifttk.get_local_config(
    section=SECTION_NAME,
    template={
        SECTION_NAME: {
            "token": str,
        },
    })


def validate_course_name(name, silent=False):
    """
    Validate the course name with an elementary heuristic (only contains
    alphanumeric characters, dash and underscore).
    """

    for c in name:
        if c.isalnum() or c in "_-":
            continue

        if silent:
            return False
        else:
            raise pylifttk.csstaff.exceptions.CourseAPIException(
                msg="Course name '{}' could be malformed.".format(name)
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