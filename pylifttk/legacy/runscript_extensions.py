
import datetime as _datetime
import glob as _glob
import typing as _typing

import dateutil.parser as _dateutil_parser

import pylifttk.legacy


# This is the path on the local file system
LEGACY_EXTENSION_PATH = "/u/{course}/assignments/*/grading/duetime.extensions"


def parse_extension_file(filepath: str) -> dict:
    """

    :param filepath:
    :return:
    """

    try:
        lines = map(str.strip, open(filepath).readlines())
    except:
        lines = []

    # janettestu 2019-11-12 23:59

    local_extensions = {}
    for line in lines:
        try:
            (student, extended_due_date) = line.split(" ", 1)
        except ValueError:
            continue

        local_extensions[student] = _dateutil_parser.parse(extended_due_date)

    return local_extensions


def parse_extensions(course: str = "cos126") -> _typing.Dict[str, _typing.Dict[str, _datetime.datetime]]:
    """

    :param course:
    :return:
    """

    glob_path = LEGACY_EXTENSION_PATH.format(course=course)
    extension_files = _glob.glob(glob_path)

    glob_path_pieces = glob_path.split("/")
    glob_path_index = glob_path_pieces.index("*")

    extensions = {}
    for filepath in extension_files:
        assignment = filepath.split("/")[glob_path_index]
        assignment_exts = parse_extension_file(filepath)

        if assignment_exts is not None and len(assignment_exts) > 0:
            extensions[assignment] = assignment_exts

    return extensions
