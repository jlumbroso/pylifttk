
from __future__ import absolute_import

import pylifttk

SECTION_NAME = "ed"

config = pylifttk.get_local_config(
    section=SECTION_NAME,
    template={
        SECTION_NAME: {
            "username": str,
            "password": str,
        },
    })