
import datetime as _datetime
import glob as _glob
import json as _json
import os as _os
import typing as _typing
import warnings as _warnings

import dateutil.parser as _dateutil_parser

import pylifttk
import pylifttk.legacy
import pylifttk.normalizations
import pylifttk.tigerfile


# This is the path on the local file system
LEGACY_EXTENSION_PATH = "/u/{course}/assignments/*/grading/duetime.extensions"

# Timezone
LEGACY_TIMEZONE = "-04:00"


def parse_local_extension_file(filepath):
    # type: (str) -> dict
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

        parsed_date = _dateutil_parser.parse(extended_due_date)
        if parsed_date is not None and parsed_date.tzinfo is None:
            parsed_date = _dateutil_parser.parse(extended_due_date + LEGACY_TIMEZONE)

        local_extensions[student] = parsed_date

    return local_extensions


def parse_local_extensions(course_name=None):
    # type: (str) -> _typing.Dict[str, _typing.Dict[str, _datetime.datetime]]
    """

    :param course_name:
    :return:
    """

    if course_name is None:
        course_name = pylifttk.get_course_name()

    glob_path = LEGACY_EXTENSION_PATH.format(course=course_name)
    extension_files = _glob.glob(glob_path)

    if len(extension_files) == 0:
        _warnings.warn(
            "It does not appear the extension parsing functionality is being run "
            "from a local course shell account. You should not expect a useful "
            "result.",
            stacklevel=2,
        )

    glob_path_pieces = glob_path.split("/")
    glob_path_index = glob_path_pieces.index("*")

    extensions = {}
    for filepath in extension_files:
        assignment = filepath.split("/")[glob_path_index]
        assignment_exts = parse_local_extension_file(filepath)

        if assignment_exts is not None and len(assignment_exts) > 0:
            extensions[assignment] = assignment_exts

    return extensions


# =======================================================================


def normalize_runscript_name_to_tigerfile_id(dropbox_id, runscript_name):
    # type: (int, str) -> int

    tigerfile_name = pylifttk.normalizations.normalize(
        runscript_name,
        pylifttk.normalizations.PyLIFTtkNormalizationType.runscript,
        pylifttk.normalizations.PyLIFTtkNormalizationType.tigerfile)

    assignments = pylifttk.tigerfile.get_assignments(dropbox_id=dropbox_id)

    for assignment in assignments:

        if assignment["name"] == tigerfile_name:
            return assignment["id"]


def preprocess_extensions_from_runscript_to_tigerfile(dropbox_id, extensions):

    students_extensions = {}

    for assignment, assignment_extensions in extensions.items():

        tigerfile_assignment_id = normalize_runscript_name_to_tigerfile_id(
            dropbox_id=dropbox_id,
            runscript_name=assignment
        )

        for student, extended_due_date in assignment_extensions.items():

            parsed_date = extended_due_date
            if type(extended_due_date) is str:
                parsed_date = _dateutil_parser.parse(extended_due_date)
                if parsed_date is not None and parsed_date.tzinfo is None:
                    parsed_date = _dateutil_parser.parse(extended_due_date + LEGACY_TIMEZONE)

            students_extensions[student] = students_extensions.get(student, dict())
            students_extensions[student][tigerfile_assignment_id] = parsed_date

    return students_extensions


# =======================================================================


def dump_local_extensions(course_name=None, course_term=None, filename=None, use_tigerfile_ids=True):
    # type: (str, str, str, bool) -> bool

    if course_name is None:
        course_name = pylifttk.get_course_name()

    if course_term is None:
        course_term = pylifttk.get_course_term()

    if filename is None:
        return False

    filename = _os.path.expanduser(filename)

    extensions = parse_local_extensions()

    if use_tigerfile_ids:

        dropbox_id = pylifttk.tigerfile.get_dropboxes(
            course_name=course_name,
            course_term=course_term,
            fetch_id=True,
        )

        processed_extensions = preprocess_extensions_from_runscript_to_tigerfile(
            dropbox_id=dropbox_id,
            extensions=extensions,
        )

        json_object = {
            "course": course_name.upper(),
            "term": course_term.upper(),
            "format": "tigerfile",
            "tigerfile_dropbox_id": dropbox_id,
            "extensions": processed_extensions,
        }

        json_output = _json.dumps(json_object, indent=2, default=str)

    else:

        json_object = {
            "course": course_name.lower(),
            "format": "runscript",
            "extensions": extensions,
        }

        if course_term is not None:
            json_object["term"] = course_term

        json_output = _json.dumps(json_object, indent=2, default=str)

    try:
        with open(filename, "w") as f:
            f.write(json_output)
            f.close()

    except Exception as e:
        return False

    return True


def load_local_extensions(filename, use_tigerfile_ids=True):
    # type: (str, bool) -> dict
    """

    :param filename:
    :param use_tigerfile_ids:
    :return:
    """

    if filename is None:
        return {}

    filename = _os.path.expanduser(filename)

    raw_json_object = _json.loads(open(filename).read())

    # parse metadata
    json_uses_tigerfile = (
        raw_json_object.get("format") == "tigerfile" and
        raw_json_object.get("tigerfile_dropbox_id") is not None
    )
    raw_extensions = raw_json_object.get("extensions", dict())

    extensions = {}

    if use_tigerfile_ids:
        # {
        #     "rahulj": {
        #         "239": "2019-10-03 23:59:00-04:00",
        #         "240": "2019-10-10 23:59:00-04:00",
        #         "238": "2019-09-26 23:59:00-04:00"
        #     },
        #     "lp4": {
        #         ...
        #     },
        #     ...
        # }

        if not json_uses_tigerfile:
            _warnings.warn(
                "Loading a tigerfile formatted extension file which does not seem to "
                "have the correct format.",
                stacklevel=2,
            )

        for student, student_extensions in raw_extensions.items():
            parsed_extensions = dict()
            for (assignment_id, date) in student_extensions.items():
                parsed_extensions[int(assignment_id)] = _dateutil_parser.parse(date)
            extensions[student] = parsed_extensions

    else:
        # {
        #     "loops": {
        #         "rahulj": "2019-10-03 23:59:00-04:00",
        #         "lp4": "2019-09-24 23:59:00-04:00",
        #         "eshen": "2020-01-01 23:59:00-04:00"
        #     },
        #     "nbody": {
        #         ...
        #     }
        #     ...
        # }

        if json_uses_tigerfile:
            _warnings.warn(
                "Loading a runscript formatted extension file which does not seem to "
                "have the correct format.",
                stacklevel=2,
            )

        for assignment_name, assignment_extensions in raw_extensions.items():
            parsed_extensions = dict()
            for (student_id, date) in assignment_extensions.items():
                parsed_extensions[student_id] = _dateutil_parser.parse(date)
            extensions[assignment_name] = parsed_extensions

    return extensions

