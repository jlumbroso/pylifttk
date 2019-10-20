
from __future__ import absolute_import

import codepost as _codepost

import pylifttk

SECTION_NAME = "codePost"

config = pylifttk.get_local_config(
    section=SECTION_NAME,
    template={
        SECTION_NAME: {
            "api_key": str,
        },
    })


_codepost.configure_api_key(config["api_key"], override=True)


# Import top-level methods
from pylifttk.codepost.macros import *