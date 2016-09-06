# -*- coding: utf-8 -*-
"""
Module that links to the calmjs.dist, for use with RJSToolchain.
"""

import logging

from os import getcwd
from os.path import join
from os.path import isdir

from calmjs.registry import get
from calmjs.dist import get_extras_calmjs
from calmjs.dist import get_module_registry_dependencies
from calmjs.dist import flatten_extras_calmjs
from calmjs.dist import flatten_module_registry_dependencies

logger = logging.getLogger(__name__)
EMPTY = 'empty:'
_default = 'all'


def identity(v):
    return v


def empty(*a, **kw):
    return EMPTY


source_map_methods_list = {
    # list of tuples of (function, filter)
    'all': (
        (flatten_module_registry_dependencies, identity),
    ),
    'explicit': (
        (flatten_module_registry_dependencies, empty),
        (get_module_registry_dependencies, identity),
    ),
    'none': None,
}

extras_calmjs_methods = {
    # function, joiner
    'all': (flatten_extras_calmjs, join),
    'explicit': (get_extras_calmjs, join),
    'empty': (flatten_extras_calmjs, empty),
    'none': None,
}


def acquire_method(methods, key, default=_default):
    return methods.get(key, methods.get(default))


def generate_transpile_source_maps(
        package_names, registries=('calmjs.module',), method=_default):
    """
    Invoke the module_registry_dependencies family of dist functions,
    with the specified registries, to produce the required source maps.

    Arguments:

    package_names
        The names of the Python package to generate the source maps for.
    registries
        The names of the registries to source the packages from.
    method
        The method to acquire the dependencies for the given module
        across all the registries specified.  Choices are between 'all',
        'explicit' or None.  Defaults to 'all'.

        'all'
            Traverse the dependency graph for the specified package to
            acquire the mappings declared for each of those modules.
        'explicit'
            Same as all, however all will be stubbed out using 'empty:'
            to prevent bundling.  Only the declared sources for the
            specified packages will be untouched.
        'none'
            Produce an empty source map.

        Defaults to 'all'.
    """

    source_map_methods = acquire_method(source_map_methods_list, method)

    if source_map_methods is None:
        return {}

    transpile_source_map = {}

    # source mapping functions loop first, to prevent subsequent
    # registries from providing key-value pairs via flatten that
    # overwrite key-value pairs set initially by the get method for a
    # key that has results for flatten but no results for get; in other
    # words, this ensures the get source mapping function get executed
    # last across all registeries, if needed.

    for source_f, n_filter in source_map_methods:
        for registry_key in registries:
            transpile_source_map.update(
                (k, n_filter(v)) for k, v in source_f(
                    package_names, registry_key=registry_key
                ).items()
            )

    return transpile_source_map


def generate_bundled_source_maps(
        package_names, working_dir=None, method=_default):
    """
    Acquire the bundled source maps through the calmjs registry system.

    Arguments:

    package_names
        The names of the package to acquire the sources for.
    working_dir
        The working directory.  Defaults to current working directory.
    method
        The method to acquire the bundled sources for the given module.
        Choices are between 'all', 'explicit', 'none, or 'empty'.

        'all'
            Traverse the dependency graph for the specified package and
            acquire the declarations. [default]
        'explicit'
            Only acquire the bundled sources declared for the specified
            package.
        'none'
            Produce an empty source map.  For requirejs, this means the
            default fallback behavior of loading from the base_dir (i.e.
            the build_dir) which will result in error on missing files.
            However this is left here for low level manipulation and/or
            usage.
        'empty'
            Same as all, but all paths will be replaced with 'empty:'.
            This effectively achieves the same effect as 'none', however
            in a way that should not error if the packages at hand have
            declared all the extra sources used in the extras_calmjs
            under the appropriate keys.

        Defaults to 'all'.
    """

    working_dir = working_dir if working_dir else getcwd()
    methods = acquire_method(extras_calmjs_methods, method)

    if methods is None:
        return {}

    acquire_extras_calmjs, joiner = methods

    # the extras keys will be treated as valid Node.js package manager
    # subdirectories.
    valid_pkgmgr_dirs = set(get('calmjs.extras_keys').iter_records())
    extras_calmjs = acquire_extras_calmjs(package_names)
    bundled_source_map = {}

    for mgr in extras_calmjs:
        if mgr not in valid_pkgmgr_dirs:
            continue
        basedir = join(working_dir, mgr)
        if not isdir(basedir):
            if extras_calmjs[mgr]:
                logger.warning(
                    "acquired extras_calmjs needs from '%s', but working "
                    "directory '%s' does not contain it; bundling may fail.",
                    mgr, working_dir
                )
            continue  # pragma: no cover

        for k, v in extras_calmjs[mgr].items():
            bundled_source_map[k] = joiner(basedir, *(v.split('/')))

    return bundled_source_map
