
from __future__ import absolute_import

import typing as _typing

import requests as _requests
import six as _six

import pylifttk.tigerfile.exceptions
import pylifttk.tigerfile.util


API_BASE_URL = "https://tigerfile.cs.princeton.edu/api/"


def request(endpoint=None, url=None, token=None):
    # type: (_typing.Optional[str], _typing.Optional[str], _typing.Optional[str]) -> _typing.DefaultDict
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
            headers={
                "Authorization": "Bearer {}".format(
                    token or pylifttk.tigerfile.util.config["token"])
            },
            # Avoid WSSE nonce error when redirecting
            allow_redirects=False,
        )

        if res.status_code == 301 and url[-1] != "/":
            return request(url="{}/".format(url))

    except _requests.RequestException as exc:
        raise pylifttk.tigerfile.exceptions.TigerfileAPIException(
            msg="Unexpected error when making a request to the Tigerfile API.",
            exc=exc,
        )

    # Handle API errors
    pylifttk.tigerfile.exceptions.handle_api_error(res)

    # If we've made this far, the result should contain a "result" key
    data = res.json()
    return data #data.get("result", dict())

