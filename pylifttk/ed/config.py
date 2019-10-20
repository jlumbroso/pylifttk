
import confuse as _confuse

import pylifttk


SECTION_NAME = "ed"


template = {
    SECTION_NAME: {
        "username": str,
        "password": str,
    },
}


def get_local_config():

    try:
        valid = pylifttk.config.get(template)

    except _confuse.NotFoundError as exc:
        raise pylifttk.PyLIFTtkConfigurationException(
            section=SECTION_NAME,
            src=exc.args,
        )

    return valid[SECTION_NAME]
