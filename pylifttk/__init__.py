"""
pylifttk

Provides a convenient toolkit of methods for use within Princeton CS' LIFT.

   Name: pylifttk
 Author: Jérémie Lumbroso
  Email: lumbroso@cs.princeton.edu
    URL: https://github.com/jlumbroso/pylifttk
License: Copyright (c) 2019 Jérémie Lumbroso, licensed under the LGPL3 license
"""


# Documentation

from pylifttk.version import __version__


# Configuration file

import os as _os
import confuse as _confuse


class PyLIFTtkConfiguration(_confuse.LazyConfig):

    def config_dir(self):

        local_config = _os.path.join(_os.getcwd(), _confuse.CONFIG_FILENAME)
        if _os.path.exists(local_config):
            return _os.getcwd()

        return super(PyLIFTtkConfiguration, self).__init__()


config = PyLIFTtkConfiguration('pylifttk', __name__)