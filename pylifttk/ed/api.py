
from __future__ import absolute_import

import json as _json
import typing as _typing

import requests as _requests
import six as _six
import wsse.client.requests.auth as _wsse_auth

import pylifttk.ed
import pylifttk.ed.exceptions


API_BASE_URL = "https://us.edstem.org/api/"


last_token = None


def get_auth_token(username=None, password=None):
    # type: (_typing.Optional[str], _typing.Optional[str]) -> _typing.Optional[str]
    """
    Obtain an authentication JWT for the Ed platform, given a valid username and
    password, provided in the configuration file.

    :param username: (Optionally) override configuration file username
    :param password: (Optionally) override configuration file password
    :return: A JWT to access the Ed platform's API.
    """
    global last_token

    url = _six.moves.urllib.parse.urljoin(
            base=API_BASE_URL,
            url="token",
        )

    try:
        res = _requests.post(
            url=url,
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
            data=_json.dumps({
                "login": username or pylifttk.ed.config["username"],
                "password": password or pylifttk.ed.config["password"]
            })
        )

    except _requests.exceptions.RequestException:
        raise

    if res.status_code != 200:
        return None

    try:
        data = res.json()
    except ValueError:
        raise

    token = data.get("token", None)
    last_token = token

    return token


def request(endpoint=None, url=None, data=None, json=None, **kwargs):
    # type: (_typing.Optional[str], _typing.Optional[str], _typing.Optional[dict], _typing.Dict) -> _typing.DefaultDict
    """
    Make a request directly to the Ed platform's API.
    """

    if last_token is None:
        get_auth_token(**kwargs)

    # If only endpoint was passed, augment with base URL
    if endpoint is not None:
        url = _six.moves.urllib.parse.urljoin(
            base=API_BASE_URL,
            url=endpoint,
        )

    headers = {
        "Sec-Fetch-Mode": "cors",
        "Origin": "https://us.edstem.org",
        "X-Token": last_token,
        "Pragma": "no-cache",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Cache-Control": "no-cache",
        "Authority": "us.edstem.org",
        "Sec-Fetch-Site": "same-origin",
    }

    try:

        if data is None and json is None:
            res = _requests.get(
                url=url,
                headers=headers,
            )

        elif json is not None:
            res = _requests.post(
                url=url,
                headers=headers,
                json=json,
            )

        else:
            res = _requests.post(
                url=url,
                headers=headers,
                data=data,
            )

        if res.status_code == 301 and url[-1] != "/":
            return request(url="{}/".format(url))

    except _requests.RequestException as exc:
        raise

    pylifttk.ed.exceptions.handle_api_error(res)

    data = res.json()

    return data
