

import pylifttk.ed.api


def get_course_id(course_name, course_term):
    user_data = pylifttk.ed.api.request(endpoint="user")

    courses = user_data["courses"]

    course_session = None
    course_year = None
    if course_term is not None:

        # Parse session
        if course_term[0] == "F":
            course_session = "Fall"
        elif course_term[0] == "S":
            course_session = "Spring"

        # Parse year
        course_year = course_term[1:]

    course_ids = []

    for record in courses:
        course_data = record["course"]

        if course_name and course_name != course_data["code"]:
            continue

        if course_session and course_session != course_data["session"]:
            continue

        if course_year and course_year != course_data["year"]:
            continue

        course_ids.append(course_data["id"])

    if len(course_ids) == 1:
        return course_ids[0]


def invite_one(course_id, name, email, tutorial, role="student"):
    result = pylifttk.ed.api.request(
        endpoint="courses/{}/invite".format(course_id),
        json={
            "invites": [
                {
                    "name": name,
                    "email": email,
                    "tutorial": tutorial
                }
            ],
            "role": role
        })

    return result is not None


def invite_many(course_id, users, role="student"):
    result = pylifttk.ed.api.request(
        endpoint="courses/{}/invite".format(course_id),
        json={
            "invites": users,
            "role": role
        })

    return result is not None


def unenroll(course_id, user_ids):
    result = pylifttk.ed.api.request(
        endpoint="courses/{}/unenroll".format(course_id),
        json={
            "user_ids": user_ids
        }
    )

    return result is not None


def users(course_id):
    result = pylifttk.ed.api.request(
        endpoint="courses/{}/admin".format(course_id)
    )

    if "users" in result:
        return result.get("users", [])