
import collections as _collections
import re as _re
import typing as _typing

import bs4 as _bs4

import pylifttk.util

import pylifttk.gradescope.api
import pylifttk.gradescope.util


ASSIGNMENT_URL_PATTERN = r"/courses/([0-9]*)/assignments/([0-9]*)$"


class GradescopeRole(pylifttk.util.DocEnum):

    # <option value="0">Student</option>
    # <option selected="selected" value="1">Instructor</option>
    # <option value="2">TA</option>
    # <option value="3">Reader</option>

    STUDENT = 0, "Student user"
    INSTRUCTOR = 1, "Instructor user"
    TA = 2, "TA user"
    READER = 3, "Reader user"


def get_assignment_grades(course_id, assignment_id, simplified=False, **kwargs):

    # Fetch the grades
    response = pylifttk.gradescope.api.request(
        endpoint="courses/{}/assignments/{}/scores.csv".format(course_id, assignment_id)
    )

    # Parse the CSV format
    grades = pylifttk.gradescope.util.parse_csv(response.content)

    # Summarize it if necessary by removing question-level data
    if simplified:
        shortened_grades = list(map(pylifttk.gradescope.util.shortened_grade_record, grades))
        return shortened_grades

    return grades


def get_course_roster(course_id, **kwargs):

    # Fetch the grades
    response = pylifttk.gradescope.api.request(
        endpoint="courses/{}/memberships.csv".format(course_id)
    )

    # Parse the CSV format
    roster = pylifttk.gradescope.util.parse_csv(response.content)

    return roster


def invite_many(course_id, role, users, **kwargs):
    # type: (int, GradescopeRole, _typing.List[_typing.Tuple[str, str]], dict) -> bool

    # Built payload
    payload = _collections.OrderedDict()
    counter = 0
    for (email, name) in users:
        payload["students[{}][name]".format(counter)] = name
        payload["students[{}][email]".format(counter)] = email
        counter += 1
    payload["role"] = role

    # Fetch the grades
    response = pylifttk.gradescope.api.request(
        endpoint="courses/{}/memberships/many".format(course_id),
        data=payload,
    )

    return response.status_code == 200


def get_courses(by_name=False):
    response = pylifttk.gradescope.api.request(endpoint="account")
    soup = _bs4.BeautifulSoup(response.content, features="html.parser")
    hrefs = list(filter(lambda s: s, map(
        lambda anchor: anchor.get("href"),
        soup.find_all("a", {"class": "courseBox"})
    )))
    course_ids = list(map(lambda href: href.split("/")[-1], hrefs))

    if by_name:
        return list(map(get_course_name, course_ids))

    return course_ids


def get_course_name(course_id):
    result = pylifttk.gradescope.api.request(endpoint="courses/{}".format(course_id))
    soup = _bs4.BeautifulSoup(result.content.decode(), features="html.parser")
    header_element = soup.find("header", {"class": "courseHeader"})
    if header_element:
        course_name = header_element.find("h1").text.replace(" ", "")

        course_term = header_element.find("div", {"class": "courseHeader--term"}).text
        course_term = course_term.replace("Fall ", "F")
        course_term = course_term.replace("Spring ", "S")
        return {"name": course_name, "term": course_term, "id": course_id}


def get_course_id(course_name, course_term):
    courses = get_courses(by_name=True)
    for course in courses:
        if course["name"] == course_name and course["term"] == course_term:
            return course["id"]


def get_course_assignments(course_id):
    # NOTE: remove "/assignments" for only active assignments?
    result = pylifttk.gradescope.api.request(endpoint="courses/{}/assignments".format(course_id))
    soup = _bs4.BeautifulSoup(result.content.decode(), features="html.parser")

    assignment_table = soup.find("table", {"class": "table-assignments"})
    anchors = assignment_table.find_all("a")

    assignments = []
    for anchor in anchors:
        url = anchor.get("href")
        if url is None or url == "":
            continue
        match = _re.match(ASSIGNMENT_URL_PATTERN, url)
        if match is None:
            continue

        assignments.append({
            "id": match.group(2),
            "name": anchor.text
        })

    return assignments


def get_course_grades(course_id, only_graded=True, use_email=True):

    # Dictionary mapping student emails to grades
    grades = {}

    gradescope_assignments = get_course_assignments(
        course_id=course_id)

    for assignment in gradescope_assignments:
        # {'id': '273671', 'name': 'Written Exam 1'}
        assignment_name = assignment["name"]
        assignment_grades = get_assignment_grades(
            course_id=course_id,
            assignment_id=assignment.get("id"),
            simplified=True)

        for record in assignment_grades:
            # {'name': 'Joe Student',
            #   'sid': 'jl27',
            #   'email': 'jl27@princeton.edu',
            #   'score': '17.75',
            #   'graded': True,
            #   'view_count': '4',
            #   'id': '22534979'}

            if only_graded and not record.get("graded", False):
                continue

            student_id = record["sid"]
            if use_email:
                student_id = record["email"]
            grade = pylifttk.util.robust_float(record.get("score"))

            # Add grade to student
            grades[student_id] = grades.get(student_id, dict())
            grades[student_id][assignment_name] = grade

    return grades


