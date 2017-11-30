# -*- coding: utf-8 -*-
"""
CalmJS RequireJS artifact generation helpers
"""

from calmjs.rjs.cli import create_spec
from calmjs.rjs.cli import default_toolchain


def complete_rjs(package_names, export_target):
    """
    Return the toolchain and a spec that when executed together, will
    result in a complete artifact using the provided package names onto
    the export_target.
    """

    return default_toolchain, create_spec(package_names, export_target)
