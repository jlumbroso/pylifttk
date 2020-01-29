from builtins import int, dict

import datetime as _datetime
import typing as _typing

import dateutil.parser as _dateutil_parser

import pylifttk.tigerfile.api
import pylifttk.tigerfile.exceptions
import pylifttk.tigerfile.util


#
ExtensionType = _typing.Union[float, _datetime.datetime]

# This type maps a student ID to a relative number of hours (past due date), or an absolute date
ExtensionsType = _typing.Optional[_typing.Dict[str, ExtensionType]]


def get_dropboxes(
        course_name: str = None,
        course_term: str = None,
        fetch_id: bool = False
) -> _typing.Optional[_typing.Union[int, dict]]:
    """

    :return:
    """
    result = pylifttk.tigerfile.api.request("dropboxes")
    result = result.get("entities", None)

    if result:
        # {'id': 1,
        #  'name': 'COS126_F2018',
        #  'hide_index': True,
        #  'course': {'id': 4, 'department': 'COS', 'course_number': '126'},
        #  'semester': {'id': 3, 'season': 'fall', 'year': 2018}}

        if course_name:
            course_name = course_name.upper()
            result = filter(
                lambda obj: "{department}{course_number}".format(
                    **obj["course"]) == course_name,
                result)

        if course_term:
            course_term = course_term.upper()
            result = filter(
                lambda obj: "{season:.1}{year}".format(
                    **obj["semester"]).upper() == course_term,
                result)

        result = list(result)

        if len(result) == 1 and fetch_id:
            return result[0]["id"]

        return result


def get_assignments(id=None, dropbox_id=None, course_name=None, course_term=None, fetch_id=False):
    # type: (_typing.Optional[int], _typing.Optional[int], _typing.Optional[str], _typing.Optional[str], bool) -> list
    """

    :return:
    """
    result = pylifttk.tigerfile.api.request("assignments")
    result = result.get("entities", None)

    if result:
        # {
        #     "id": 247,
        #     "name": "TSP Leaderboard",
        #     "description": "TSP Leaderboard",
        #     "use_date_control": false,
        #     "due_date": "2019-12-02T23:59:00-05:00",
        #     "submission_enabled": true,
        #     "submission_open_date": "2018-09-12T21:21:00-04:00",
        #     "submission_close_date": "2018-09-12T21:21:00-04:00",
        #     "access_enabled": true,
        #     "access_open_date": "2018-09-12T21:21:00-04:00",
        #     "access_close_date": "2018-09-12T21:21:00-04:00",
        #     "dropbox": {
        #         "id": 28,
        #         "name": "COS126_F2019"
        #     },
        #     "assignment_filenames": [
        #         {
        #             "id": 572,
        #             "name": "TSP.java",
        #             "optional": false
        #         },
        #         {
        #             "id": 573,
        #             "name": "leaderboard.txt",
        #             "optional": false
        #         }
        #     ],
        #     "assignment_files": [],
        #     "submission_attempts_max": 0,
        #     "allow_arbitrary_uploads": true,
        #     "group_submission": true,
        #     "allow_not_done": true,
        #     "students_per_group_min": 1,
        #     "students_per_group_max": 2,
        #     "script_enabled": true,
        #     "created": "2018-09-12T20:06:55-04:00",
        #     "updated": "2019-09-12T18:35:29-04:00"
        # },

        if id:
            result = filter(
                lambda obj: obj["id"] == id,
                result)

        if dropbox_id:
            result = filter(
                lambda obj: obj["dropbox"]["id"] == dropbox_id,
                result)

        if course_name:
            course_name = course_name.upper()
            result = filter(
                lambda obj: course_name in obj["dropbox"]["name"],
                result)

        if course_term:
            course_term = course_term.upper()
            result = filter(
                lambda obj: course_term in obj["dropbox"]["name"],
                result)

        result = list(result)

        if len(result) == 1 and fetch_id:
            return result[0]["id"]

        return result


def get_assignments_summary(dropbox_id):
    assignments = [
        a
        for a in pylifttk.tigerfile.get_assignments(dropbox_id=dropbox_id)
        if "Assignment" in a.get("description")
    ]

    assignments_summary = {}
    for a in assignments:
        record = {}
        record["id"] = a["id"]
        record["name"] = a["name"]
        record["due"] = _dateutil_parser.parse(a["due_date"])
        record["filenames"] = list(map(
            lambda x: x["name"],
            filter(lambda x: not x["optional"],
                   a["assignment_filenames"])))
        assignments_summary[record["id"]] = record

    return assignments_summary


def get_users(dropbox_id):
    # type: (int) -> dict
    """

    :return:
    """
    result = pylifttk.tigerfile.api.request("dropboxes/{}/users".format(dropbox_id))
    return result.get("entities", None)


def get_roles(dropbox_id):
    # type: (int) -> dict
    """

    :return:
    """
    result = pylifttk.tigerfile.api.request("dropboxes/{}/roles".format(dropbox_id))
    return result.get("entities", None)

def get_memberships(assignment_id, simplified=False):
    # type: (int) -> dict
    """

    :return:
    """
    result = pylifttk.tigerfile.api.request("assignments/{}/memberships".format(assignment_id))
    entities = result.get("entities", None)

    if entities is not None and simplified:
        # {
        #     "id": 22684,
        #     "user": {
        #         "id": 21443,
        #         "username": "bragan",
        #         "first_name": "Baileys",
        #         "last_name": "Ragan",
        #         "_links": {
        #             "self": {
        #                 "href": "\/users\/21443"
        #             }
        #         }
        #     },
        #     "submission": {
        #         "id": "867fc467e560aa92da36c4b73477431d"
        #     },
        #     "confirmed": true,
        #     "notified": true
        # },
        entities = {
            row.get("user", dict()).get("username") : row.get("submission", dict()).get("id")
            for row in entities
        }

    return entities

def get_students(dropbox_id):
    students = []

    roles = pylifttk.tigerfile.get_roles(dropbox_id=dropbox_id)

    for role in roles:
        # {'id': 3883,
        #   'user': {'id': 2085, 'username': 'aa26'},
        #   'dropbox': {'id': 28, 'name': 'COS126_F2019'},
        #   'role': 'ROLE_STUDENT',
        #   'precept': 'P08',
        #   'subscriptions': []}
        if role.get("role") != 'ROLE_STUDENT':
            continue
        netid = role.get("user").get("username")
        user_id = role.get("user").get("id")
        students.append((user_id, netid))

    return students

def get_submissions(dropbox_id, user_id):
    # type: (int, int) -> dict
    """

    :return:
    """
    result = pylifttk.tigerfile.api.request(
        "dropboxes/{}/users/{}/submissions".format(dropbox_id, user_id))
    return result.get("entities", None)


def compute_student_lateness(dropbox_id, user_id, assignments_summary=None, extensions=None):
    # type: (int, int, _typing.Optional[dict], _typing.Optional[ExtensionType]) ->_typing.Dict[int, _datetime.timedelta]
    """

    :param dropbox_id:
    :param user_id:
    :param assignments_summary:
    :param extensions:
    :return:
    """

    if assignments_summary is None:
        assignments_summary = get_assignments_summary(dropbox_id)

    submissions = pylifttk.tigerfile.get_submissions(
        dropbox_id=dropbox_id,
        user_id=user_id,
    )

    student_lateness = {}

    if extensions is None:
        extensions = dict()

    for sub in submissions:
        a_id = sub["assignment"]["id"]

        # Check if this is an assignment we are interested in
        if a_id not in assignments_summary:
            continue

        # Check if there are any files submitted
        if len(sub["submission_files"]) == 0:
            continue

        a_info = assignments_summary[a_id]

        student_ts = None
        file_ts = None
        for file in sub["submission_files"]:
            file_ts = _dateutil_parser.parse(file["updated"])
            if student_ts is None or student_ts < file_ts:
                student_ts = file_ts

        due_date = a_info["due"]

        # Check for an extension
        if a_id in extensions:

            a_ext = extensions.get(a_id)

            if type(a_ext) is float:
                # extension in relative hours
                due_date = due_date + _datetime.timedelta(seconds=a_ext * 60.0 * 60.0)

            elif type(a_ext) is _datetime.datetime:
                # extension is absolute datetime
                due_date = a_ext

        delay = student_ts - due_date

        if delay > _datetime.timedelta(seconds=0):
            student_lateness[a_id] = delay

    return student_lateness


def compute_dropbox_lateness(course_name, course_term, extensions=None):
    # type: (str, str, ExtensionsType) -> _typing.Optional[_typing.Dict[str, _typing.Dict[int, _datetime.timedelta]]]
    """

    :param course_name:
    :param course_term:
    :param extensions:
    :return:
    """

    dropbox_id = pylifttk.tigerfile.get_dropboxes(
        course_name=course_name,
        course_term=course_term,
        fetch_id=True
    )
    if dropbox_id is None:
        return

    students = pylifttk.tigerfile.get_students(dropbox_id=dropbox_id)

    assignments_summary = get_assignments_summary(dropbox_id=dropbox_id)
    lateness = {}

    if extensions is None:
        extensions = dict()

    for (user_id, netid) in students:
        student_extensions = extensions.get(netid, dict())
        record = compute_student_lateness(
            dropbox_id=dropbox_id,
            user_id=user_id,
            assignments_summary=assignments_summary,
            extensions=student_extensions,
        )
        if record and len(record) > 0:
            lateness[netid] = record

    return lateness


GRACE_PERIOD = 2 * 60 * 60  # two hours in seconds


def timedelta_to_lateness(dt, by_hours=False):
    if dt is None or type(dt) is str or type(dt) is int:
        return dt

    total_seconds = dt.days * 24 * 60 * 60 + dt.seconds

    if total_seconds < GRACE_PERIOD:
        return 0.0

    total_minutes = total_seconds / 60
    total_hours = total_minutes / 60
    total_days = total_hours / 24

    if by_hours:
        return round(total_hours, 2)
    else:
        return round(total_days, 2)


def compute_dropbox_lateness_totals(course_name, course_term, by_hours=False, extensions=None):
    # type: (str, str, bool, ExtensionsType) -> _typing.Dict[str, float]

    assignments = sorted(filter(
        lambda rec: "assignment" in rec.get("description", "").lower(),
        pylifttk.tigerfile.macros.get_assignments(
            course_name=course_name,
            course_term=course_term)),
        key=lambda rec: rec.get("due_date"))

    lateness = pylifttk.tigerfile.macros.compute_dropbox_lateness(
        course_name=course_name,
        course_term=course_term,
        extensions=extensions)

    lateness_totals = {}
    for (student, record) in lateness.items():
        total = timedelta_to_lateness(sum(record.values(), start=_datetime.timedelta(0)), by_hours=by_hours)
        lateness_totals[student] = total

    return lateness_totals


def compute_dropbox_lateness_csv_string(course_name, course_term, by_hours=False, extensions=None):
    # type: (str, str, bool, ExtensionsType) -> str
    """

    :param course_name:
    :param course_term:
    :param by_hours:
    :param extensions:
    :return:
    """

    assignments = sorted(filter(
        lambda rec: "assignment" in rec.get("description", "").lower(),
        pylifttk.tigerfile.macros.get_assignments(
            course_name=course_name,
            course_term=course_term)),
        key=lambda rec: rec.get("due_date"))

    lateness = pylifttk.tigerfile.macros.compute_dropbox_lateness(
        course_name=course_name,
        course_term=course_term,
        extensions=extensions)

    headers = ['"Username"'] + list(map(lambda rec: '"{}"'.format(rec.get("name")), assignments)) + ['"Total"']
    lines = []
    for (student, record) in lateness.items():
        line_fields = ['"{}"'.format(student)] + list(map(
            lambda rec: str(timedelta_to_lateness(record.get(rec["id"], ""), by_hours=by_hours)), assignments))
        total = str(timedelta_to_lateness(sum(record.values(), start=_datetime.timedelta(0)), by_hours=by_hours))
        line_fields.append(total)
        lines.append(line_fields)
    lines = sorted(lines)
    csv_string = "\n".join(list(map(lambda f: ",".join(f), ([headers] + lines))))

    return csv_string
