
import datetime as _datetime
import glob as _glob
import json as _json
import typing as _typing

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
            parsed_date = _dateutil_parser.parse(extended_due_date + LEGACY_TIMEZONE).tzinfo

        local_extensions[student] = parsed_date

    return local_extensions


def parse_local_extensions(course_name=None):
    # type: (str) -> _typing.Dict[str, _typing.Dict[str, _datetime.datetime]]
    """

    :param course:
    :return:
    """

    if course_name is None:
        course_name = pylifttk.get_course_name()

    glob_path = LEGACY_EXTENSION_PATH.format(course=course_name)
    extension_files = _glob.glob(glob_path)

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
                    parsed_date = _dateutil_parser.parse(extended_due_date + LEGACY_TIMEZONE).tzinfo

            students_extensions[student] = students_extensions.get(student, dict())
            students_extensions[student][tigerfile_assignment_id] = parsed_date

    return students_extensions


# =======================================================================


def dump_local_extensions(course_name=None, course_term=None, filename=None):
    # type: (str, str, str) -> bool

    if course_name is None:
        course_name = pylifttk.get_course_name()

    if course_term is None:
        course_term = pylifttk.get_course_term()

    if filename is None:
        return False

    dropbox_id = pylifttk.tigerfile.get_dropboxes(
        course_name=course_name,
        course_term=course_term,
        fetch_id=True,
    )

    extensions = parse_local_extensions()

    processed_extensions = preprocess_extensions_from_runscript_to_tigerfile(
        dropbox_id=dropbox_id,
        extensions=extensions,
    )

    json_output = _json.dumps(processed_extensions, indent=2, default=str)

    try:
        with open(filename, "w") as f:
            f.write(json_output)
            f.close()
    except Exception as e:
        return False

    return True

