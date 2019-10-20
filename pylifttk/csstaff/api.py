
from __future__ import absolute_import

import typing as _typing

import requests as _requests
import six as _six
import wsse.client.requests.auth as _wsse_auth

import pylifttk.csstaff.exceptions
import pylifttk.csstaff.util


API_BASE_URL = "https://adm.cs.princeton.edu/api/v1/"


def request(endpoint=None, url=None):
    # type: (_typing.Optional[str], _typing.Optional[str]) -> _typing.DefaultDict
    """
    Make a request directly to the Princeton CSStaff's Course API.
    """

    # If only endpoint was passed, augment with base URL
    if endpoint is not None:
        url = _six.moves.urllib.parse.urljoin(
            base=API_BASE_URL,
            url=endpoint,
        )

    try:
        res = _requests.get(
            url=url,
            auth=_wsse_auth.WSSEAuth(
                username=pylifttk.csstaff.util.config["username"],
                password=pylifttk.csstaff.util.config["password"]),
            # Avoid WSSE nonce error when redirecting
            allow_redirects=False,
        )

        if res.status_code == 301 and url[-1] != "/":
            return request(url="{}/".format(url))

    except _requests.RequestException as exc:
        raise pylifttk.csstaff.exceptions.CourseAPIException(
            msg="Unexpected error when making a request to the Course API.",
            exc=exc,
        )

    # Handle API errors
    pylifttk.csstaff.exceptions.handle_api_error(res)

    # If we've made this far, the result should contain a "result" key
    data = res.json()
    return data.get("result", dict())

