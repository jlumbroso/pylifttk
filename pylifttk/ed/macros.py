

import pylifttk.ed.api as _api


def invite_one(course_id, name, email, tutorial, role="student"):
    result = _api.request(
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
    result = _api.request(
        endpoint="courses/{}/invite".format(course_id),
        json={
            "invites": [
                users
            ],
            "role": role
        })

    return result is not None


def unenroll(course_id, user_ids):
    result = _api.request(
        endpoint="courses/{}/unenroll".format(course_id),
        json={
            "user_ids": user_ids
        }
    )

    return result is not None


def users(course_id):
    result = _api.request(endpoint="courses/{}/admin".format(course_id))

    if "users" in result:
        return result.get("users", [])