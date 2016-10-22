# -*- coding: utf-8 -*-
import unittest
from os.path import exists

# This is for emulating absent calmjs.dev module
try:
    import builtins
except ImportError:  # pragma: no cover
    # python 2
    import __builtin__ as builtins

try:
    from calmjs.dev import karma
except ImportError:  # pragma: no cover
    karma = None

from calmjs.exc import ToolchainAbort
from calmjs.registry import get
from calmjs.toolchain import Spec
from calmjs.utils import pretty_logging

from calmjs.rjs.dev import karma_requirejs
from calmjs.rjs.registry import RJS_LOADER_PLUGIN_REGISTRY_NAME

from calmjs.testing.mocks import StringIO
from calmjs.testing.utils import mkdtemp
from calmjs.testing.utils import stub_item_attr_value


class KarmaAbsentTestCase(unittest.TestCase):
    """
    Test the injection of requirejs specific idioms into the karma
    test runner setup runtime.
    """

    def test_no_calmjs_dev(self):
        __import__ = builtins.__import__

        def import_(name, *a, **kw):
            if name == 'calmjs.dev':
                raise ImportError("No module named 'calmjs.dev'")
            return __import__(name, *a, **kw)

        stub_item_attr_value(self, builtins, '__import__', import_)
        spec = Spec()

        # just to cover the fake import above
        from calmjs.toolchain import Spec as Spec_
        self.assertIs(Spec, Spec_)

        with pretty_logging(stream=StringIO()) as s:
            karma_requirejs(spec)

        self.assertNotIn('karma_config', spec)
        self.assertIn(
            "package 'calmjs.dev' not available; cannot apply requirejs",
            s.getvalue(),
        )


@unittest.skipIf(karma is None, 'calmjs.dev or its karma module not available')
class KarmaTestCase(unittest.TestCase):

    def test_karma_setup_empty(self):
        spec = Spec()
        with pretty_logging(stream=StringIO()) as s:
            with self.assertRaises(ToolchainAbort):
                karma_requirejs(spec)

        self.assertNotIn('karma_config', spec)
        self.assertIn("'karma_config' not provided by spec", s.getvalue())

    def test_karma_setup_missing_build_dir(self):
        spec = Spec(karma_config={})
        with pretty_logging(stream=StringIO()) as s:
            with self.assertRaises(ToolchainAbort):
                karma_requirejs(spec)

        self.assertNotIn('build_dir', spec)
        self.assertIn("'build_dir' not provided by spec", s.getvalue())

    def test_karma_setup_basic_empty_case(self):
        spec = Spec(
            karma_config=karma.build_base_config(),
            build_dir=mkdtemp(self),
        )

        with pretty_logging(stream=StringIO()) as s:
            karma_requirejs(spec)

        self.assertIn(
            "no rjs loader plugin registry provided in spec; "
            "falling back to default registry 'calmjs.rjs.loader_plugin'",
            s.getvalue()
        )

        # ensure the karma bits are added.
        self.assertTrue(exists(spec['karma_requirejs_test_config']))
        self.assertTrue(exists(spec['karma_requirejs_test_script']))
        self.assertIn('requirejs', spec['karma_config']['frameworks'])

    def test_karma_setup_files(self):
        karma_config = karma.build_base_config()
        karma_config['files'] = ['example/package/lib.js']
        spec = Spec(
            karma_config=karma_config,
            build_dir=mkdtemp(self),
            rjs_loader_plugin_registry=get(RJS_LOADER_PLUGIN_REGISTRY_NAME),
        )

        with pretty_logging(stream=StringIO()) as s:
            karma_requirejs(spec)

        self.assertNotIn("no rjs loader plugin registry ", s.getvalue())

        self.assertEqual(spec['karma_config']['files'], [
            spec['karma_requirejs_test_config'],
            spec['karma_requirejs_test_script'],
            {
                'pattern': 'example/package/lib.js',
                'included': False,
            },
        ])