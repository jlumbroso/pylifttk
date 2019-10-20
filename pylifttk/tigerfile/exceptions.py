
import typing as _typing

import requests as _requests



class TigerfileAPIException(Exception):

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

        super(TigerfileAPIException, self).__init__(self.message)


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

    raise TigerfileAPIException(
        msg="Unknown HTTP error, see source exception headers.",
        **data)
