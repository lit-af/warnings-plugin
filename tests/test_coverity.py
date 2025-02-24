import filecmp
import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

import pytest

from mlx.warnings import Finding, WarningsPlugin, warnings_wrapper

TEST_IN_DIR = Path(__file__).parent / "test_in"
TEST_OUT_DIR = Path(__file__).parent / "test_out"


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


@patch.dict(os.environ, {
    "MIN_UNCLASSIFIED": "8", "MAX_UNCLASSIFIED": "8",
    "MIN_INTENTIONAL": "1", "MAX_INTENTIONAL": "1",
    "MIN_FALSE_POSITIVE": "2", "MAX_FALSE_POSITIVE": "2",
})
class TestCoverityWarnings(TestCase):
    @pytest.fixture(autouse=True)
    def caplog(self, caplog):
        self.caplog = caplog

    def setUp(self):
        Finding.fingerprints = {}
        self.warnings = WarningsPlugin()
        self.warnings.activate_checker_name("coverity", True, None)

    def test_no_warning_normal_text(self):
        dut = "This should not be treated as warning"
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 0)

    def test_no_warning_but_still_command_output(self):
        dut = "src/something/src/somefile.c:82: 1. misra_violation: Essential type of the left hand operand \"0U\" "\
              "(unsigned) is not the same as that of the right operand \"1U\"(signed)."
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        dut = "/src/somefile.c:82: CID 113396 (#2 of 2): Coding standard violation (MISRA C-2012 Rule 10.1): "\
              "Unclassified, Unspecified, Undecided, owner is nobody, first detected on 2017-07-27."
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertEqual([f"{dut}"], self.caplog.messages)

    def test_single_warning_count_one(self):
        dut1 = "/src/somefile.c:80: CID 113396 (#1 of 2): Coding standard violation (MISRA C-2012 Rule 10.1): "\
               "Unclassified, Unspecified, Undecided, owner is nobody, first detected on 2017-07-27."
        dut2 = "/src/somefile.c:82: CID 113396 (#2 of 2): Coding standard violation (MISRA C-2012 Rule 10.1): "\
               "Unclassified, Unspecified, Undecided, owner is nobody, first detected on 2017-07-27."
        self.warnings.check(dut1)
        self.warnings.check(dut2)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertEqual([f"{dut2}"], self.caplog.messages)

    def test_single_warning_real_output(self):
        dut1 = "/src/somefile.c:80: CID 113396 (#1 of 2): Coding standard violation (MISRA C-2012 Rule 10.1): "\
               "Unclassified, Unspecified, Undecided, owner is nobody, first detected on 2017-07-27."
        dut2 = "/src/somefile.c:82: CID 113396 (#2 of 2): Coding standard violation (MISRA C-2012 Rule 10.1): "\
               "Unclassified, Unspecified, Undecided, owner is nobody, first detected on 2017-07-27."
        dut3 = "src/something/src/somefile.c:82: 1. misra_violation: Essential type of the left hand operand \"0U\" "\
               "(unsigned) is not the same as that of the right operand \"1U\"(signed)."
        self.warnings.check(dut1)
        self.warnings.check(dut2)
        self.warnings.check(dut3)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertEqual([f"{dut2}"], self.caplog.messages)

    def test_code_quality_without_config(self):
        filename = "coverity_cq.json"
        out_file = str(TEST_OUT_DIR / filename)
        ref_file = str(TEST_IN_DIR / filename)
        retval = warnings_wrapper([
            "--coverity",
            "--code-quality", out_file,
            str(TEST_IN_DIR / "coverity_full.txt"),
        ])
        self.assertEqual(11, retval)
        self.assertTrue(filecmp.cmp(out_file, ref_file))

    def test_code_quality_with_config_pass(self):
        filename = "coverity_cq.json"
        out_file = str(TEST_OUT_DIR / filename)
        ref_file = str(TEST_IN_DIR / filename)
        retval = warnings_wrapper([
            "--code-quality", out_file,
            "--config", str(TEST_IN_DIR / "config_example_coverity.yml"),
            str(TEST_IN_DIR / "coverity_full.txt"),
        ])
        self.assertEqual(0, retval)
        self.assertTrue(filecmp.cmp(out_file, ref_file))

    @patch.dict(os.environ, {
        "MIN_UNCLASSIFIED": "11", "MAX_UNCLASSIFIED": "-1",
        "MIN_FALSE_POSITIVE": "0", "MAX_FALSE_POSITIVE": "1",
    })
    def test_code_quality_with_config_fail(self):
        filename = "coverity_cq.json"
        out_file = str(TEST_OUT_DIR / filename)
        ref_file = str(TEST_IN_DIR / filename)
        retval = warnings_wrapper([
            "--code-quality", out_file,
            "--config", str(TEST_IN_DIR / "config_example_coverity.yml"),
            str(TEST_IN_DIR / "coverity_full.txt"),
        ])
        self.assertEqual(10, retval)  # 8 + 2 not within range 6 and 7
        self.assertTrue(filecmp.cmp(out_file, ref_file))
