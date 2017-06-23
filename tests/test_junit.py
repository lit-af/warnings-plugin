from unittest import TestCase

from mlx.warnings import WarningsPlugin


class TestJUnitFailures(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin()

    def test_no_warning(self):
        self.warnings.check_junit_failures('<testcase classname="dummy_class" name="dummy_name" />')
        self.assertEqual(self.warnings.return_junit_failures(), 0)

    def test_single_warning(self):
        self.warnings.check_junit_failures('<testcase classname="dummy_class" name="dummy_name"><failure message="some random message from test case" /></testcase>')
        self.assertEqual(self.warnings.return_junit_failures(), 1)

    def test_single_warning_mixed(self):
        self.warnings.check_junit_failures('<testcase classname="dummy_class" name="dummy_name1" />')
        self.warnings.check_junit_failures('<testcase classname="dummy_class" name="dummy_name2"><failure message="some random message from test case" /></testcase>')
        self.warnings.check_junit_failures('<testcase classname="dummy_class" name="dummy_name3" />')

        self.assertEqual(self.warnings.return_junit_failures(), 1)

    def test_dual_warning(self):
        self.warnings.check_junit_failures('<testcase classname="dummy_class" name="dummy_name1"><failure message="some random message from test case 1" /></testcase><testcase classname="dummy_class" name="dummy_name2"><failure message="some random message from test case 2" /></testcase>')
        self.assertEqual(self.warnings.return_junit_failures(), 2)

