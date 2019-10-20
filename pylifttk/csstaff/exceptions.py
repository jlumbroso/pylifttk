
import typing as _typing

import requests as _requests


# List from https://csguide.cs.princeton.edu/publishing/course-api

COURSE_API_ERRORS = {
    0: "generic error - no specific meaning provided",
    1: "API account has expired",
    2: "client IP address is invalid (not on the whitelist)",
    3: "API rate limit quota reached for the day",
    4: "HTTP authentication header required for WSSE auth is missing",
    5: "part of the header is malformed / missing",
    6: "format of the 'Created' date field in the token is incorrect",
    7: ("date/time of the token is in the future, compared to the " +
        "server's current time"),
    8: ("token has expired (there is a limited window of time to use " +
        "a WSSE token after it has been created)"),
    9: "username or password digest is invalid",
    10: "the nonce in the request was previously used"
}


class CourseAPIException(Exception):

    def __init__(self, **kv):

        # Store all keyword args as internal metadata

        self.data = kv

        # Build the message

        self.message = ""

        if "msg" in self.data:
            self.message += kv['msg'] + "\n\n"
            del self.data["msg"]

        if len(self.data) > 0:
            self.message += ("Additional information:\n\n" +
                             "\n".join("  %s: %r" % x for x in kv.items()))

        # Call parent class constructor

        super(CourseAPIException, self).__init__(self.message)


def get_external_ip():
    # type: () -> _typing.Optional[_typing.AnyStr]
    try:
        ip = _requests.get('https://api.ipify.org').text
        return ip
    except _requests.RequestException:
        return None


def handle_api_error(res):
    # type: (_requests.Response) -> _typing.Optional[_typing.Dict]

    # Exit on malformed argument or successful status code
    if res is None or res.status_code == 200:
        return

    # Assume there is an error and build information dictionary
    data = {
        "url": res.url,
        "http_code": res.status_code,
        "http_msg": res.content,
        "json_msg": None,
        "external_ip": get_external_ip(),
    }

    # data["username"] = username or ROSTER_USER
    # data["src_exception"] = err

    # Try to get JSON error.
    try:
        data["json_msg"] = res.json()

        # No need for plain version if successful
        del data["http_msg"]
    except ValueError:
        # Could not parse, so it's probably not JSON.
        pass

    if data["http_code"] == 404:
        # Not found
        raise CourseAPIException(
            msg="Endpoint '{}' does not exist".format(data["url"]),
            **data
        )

    elif data["json_msg"] is not None and "error" in data["json_msg"]:
        # Authorization issue
        course_api_code = data["json_msg"]["error"]["error_code"]
        course_api_msg = COURSE_API_ERRORS.get(course_api_code,
                                               "Unknown error: {}".format(
                                                   data["json_msg"]
                                               ))
        raise CourseAPIException(
            msg="Authorization error {}: {}".format(
                course_api_code, course_api_msg),
            **data
        )

    elif data["http_code"] == 401:
        # Authentication issue
        raise CourseAPIException(
            msg=("Authentication failed, check that your authentication "
                 "header is valid and confirm with CS staff that your "
                 "account is active (csstaff@cs.princeton.edu)."),
            **data
        )

    elif data["http_code"] == 401:
        # Authentication issue
        raise CourseAPIException(
            msg=("There was an unexpected server error. Please report as "
                 "much information as you can about your request to CS"
                 "staff (csstaff@cs.princeton.edu)."),
            **data
        )

    raise CourseAPIException(
        msg="Unknown HTTP error, see source exception headers.",
        **data)
