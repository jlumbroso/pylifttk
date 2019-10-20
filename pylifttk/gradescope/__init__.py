
from __future__ import absolute_import

import pylifttk

SECTION_NAME = "gradescope"

config = pylifttk.get_local_config(
    section=SECTION_NAME,
    template={
        SECTION_NAME: {
            "username": str,
            "password": str,
        },
    })


# Import top-level methods
from pylifttk.gradescope.macros import *