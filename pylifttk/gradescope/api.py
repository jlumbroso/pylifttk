
from __future__ import absolute_import

import json as _json
import typing as _typing

import bs4 as _bs4
import requests as _requests
import six as _six
import wsse.client.requests.auth as _wsse_auth

import pylifttk.gradescope
import pylifttk.gradescope.exceptions


BASE_URL = "https://www.gradescope.com"


last_cookies = None


def get_auth_cookies(username=None, password=None, **kwargs):
    # type: (_typing.Optional[str], _typing.Optional[str], _typing.Dict) -> _typing.Optional[dict]
    global last_cookies

    session = _requests.sessions.session()

    # Step 1: Get an "authenticity token" and start the GradeScope session

    try:
        response = session.get(BASE_URL)
    except _requests.RequestException:
        return

    soup = _bs4.BeautifulSoup(response.content, features="html.parser")
    authenticity_token = soup.find("input", {"name": "authenticity_token"}).get("value")

    # Step 2: Login with credentials and get signed token

    url = _six.moves.urllib.parse.urljoin(
        base=BASE_URL,
        url="login",
    )

    try:
        response = session.post(
            url=url,
            allow_redirects=False,
            headers={
                "Connection": "keep-alive",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Origin": BASE_URL,
                "Upgrade-Insecure-Requests": "1",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/77.0.3865.120 Safari/537.36"),
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Accept": "text/html,application/xhtml+xml,application/xml",
                "Sec-Fetch-Site": "same-origin",
                "Referer": BASE_URL,
            },
            data={
                "utf8": "✓",
                "authenticity_token": authenticity_token,
                "session[email]": username or pylifttk.gradescope.config["username"],
                "session[password]": password or pylifttk.gradescope.config["password"],
                "session[remember_me]": "0,1",
                "commit": "Log+In",
                "session[remember_me_sso]": "0",
            },
        )
    except _requests.RequestException:
        return

    # Step 3: Inspect cookies to make sure we are logged in

    if response.status_code in [200, 302]:
        cookies = response.cookies
        cookies_string = "; ".join(
            list(map(lambda cookie: "{name}={value}".format(
                name=cookie.name, value=cookie.value),
                     cookies)))

        if "_gradescope_session" in cookies and "signed_token" in cookies:
            data = {
                "authenticity_token": authenticity_token,
                "_gradescope_session": cookies["_gradescope_session"],
                "signed_token": cookies["signed_token"],
                "cookies": cookies,
                "cookies_string": cookies_string
            }
            last_cookies = data
            return data


def request(endpoint=None, url=None, data=None, json=None, **kwargs):
    # type: (_typing.Optional[str], _typing.Optional[str], _typing.Optional[_typing.Union[str, dict]], _typing.Optional[dict], dict) -> _requests.Response
    """
    Make a request directly to the Ed platform's API.
    """

    if last_cookies is None:
        get_auth_cookies(**kwargs)

    # If only endpoint was passed, augment with base URL
    if endpoint is not None:
        url = _six.moves.urllib.parse.urljoin(
            base=BASE_URL,
            url=endpoint,
        )

    headers = {
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/77.0.3865.120 Safari/537.36"),
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Accept": "text/html,application/xhtml+xml,application/xml",
        "Sec-Fetch-Site": "same-origin",
        "Referer": BASE_URL,
        "Cookie": last_cookies.get("cookies_string"),
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

    pylifttk.gradescope.exceptions.handle_api_error(res)

    return res
