from unittest import TestCase

from mlx.warnings import WarningsPlugin


class TestDoxygenWarnings(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin()
        self.warnings.activate_checker_name('doxygen', True)

    def test_no_warning(self):
        dut = 'This should not be treated as warning'
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        dut = 'testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"'
        with self.assertLogs(logger="doxygen", level="INFO") as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertIn(f"INFO:doxygen:{dut}", fake_out.output)

    def test_single_warning_mixed(self):
        dut1 = 'This1 should not be treated as warning'
        dut2 = 'testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"'
        dut3 = 'This should not be treated as warning2'
        with self.assertLogs(logger="doxygen", level="INFO") as fake_out:
            self.warnings.check(dut1)
            self.warnings.check(dut2)
            self.warnings.check(dut3)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertIn(f"INFO:doxygen:{dut2}", fake_out.output)

    def test_multiline(self):
        duterr1 = "testfile.c:6: warning: group test: ignoring title \"Some test functions\" that does not match old title \"Some freaky test functions\"\n"
        duterr2 = "testfile.c:8: warning: group test: ignoring title \"Some test functions\" that does not match old title \"Some freaky test functions\"\n"
        dut = "This1 should not be treated as warning\n"
        dut += duterr1
        dut += "This should not be treated as warning2\n"
        dut += duterr2
        with self.assertLogs(logger="doxygen", level="INFO") as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 2)
        self.assertIn(f"INFO:doxygen:{duterr1.strip()}", fake_out.output)
        self.assertIn(f"INFO:doxygen:{duterr2.strip()}", fake_out.output)

    def test_git_warning(self):
        duterr1 = "testfile.c:6: warning: group test: ignoring title \"Some test functions\" that does not match old title \"Some freaky test functions\"\n"
        duterr2 = "testfile.c:8: warning: group test: ignoring title \"Some test functions\" that does not match old title \"Some freaky test functions\"\n"
        dut = "warning: notes ref refs/notes/review is invalid should not be treated as warning\n"
        dut += duterr1
        dut += "This should not be treated as warning2\n"
        dut += duterr2
        with self.assertLogs(logger="doxygen", level="INFO") as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 2)
        self.assertIn(f"INFO:doxygen:{duterr1.strip()}", fake_out.output)
        self.assertIn(f"INFO:doxygen:{duterr2.strip()}", fake_out.output)

    def test_sphinx_deprecation_warning(self):
        duterr1 = "testfile.c:6: warning: group test: ignoring title \"Some test functions\" that does not match old title \"Some freaky test functions\"\n"
        dut = "/usr/local/lib/python3.5/dist-packages/sphinx/application.py:402: RemovedInSphinx20Warning: app.info() "\
            "is now deprecated. Use sphinx.util.logging instead. RemovedInSphinx20Warning)\n"
        dut += duterr1
        with self.assertLogs(logger="doxygen", level="INFO") as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertIn(f"INFO:doxygen:{duterr1.strip()}", fake_out.output)

    def test_doxygen_warnings_txt(self):
        dut_file = 'tests/test_in/doxygen_warnings.txt'
        with open(dut_file) as open_file:
            self.warnings.check(open_file.read())
        self.assertEqual(self.warnings.return_count(), 22)
