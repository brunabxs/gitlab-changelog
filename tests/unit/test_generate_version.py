#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from gitlab_changelog import generate_version, InvalidVersion


class TestGenerateVersion(unittest.TestCase):
    """This class tests the generate_version method"""

    def test_invalid_version_must_raise_error(self):
        with self.assertRaises(InvalidVersion):
            generate_version(version='abc')

    def test_no_version_and_version_type_rc_must_return_major_0_minor_0_patch_1_rc_1(self):
        actual = generate_version(version='', version_type='rc')
        self.assertEqual(actual, '0.0.1-rc.1')

    def test_no_version_and_version_type_patch_must_return_major_0_minor_0_patch_1_without_rc(self):
        actual = generate_version(version='', version_type='patch')
        self.assertEqual(actual, '0.0.1')

    def test_no_version_and_version_type_minor_must_return_major_0_minor_1_patch_0_without_rc(self):
        actual = generate_version(version='', version_type='minor')
        self.assertEqual(actual, '0.1.0')

    def test_no_version_and_version_type_major_must_return_major_1_minor_0_patch_0_without_rc(self):
        actual = generate_version(version='', version_type='major')
        self.assertEqual(actual, '1.0.0')

    def test_non_rc_version_and_version_type_rc_must_add_rc_1(self):
        actual = generate_version(version='1.2.3', version_type='rc')
        self.assertEqual(actual, '1.2.3-rc.1')

    def test_non_rc_version_and_version_type_patch_must_only_increment_patch(self):
        actual = generate_version(version='1.2.3', version_type='patch')
        self.assertEqual(actual, '1.2.4')

    def test_non_rc_version_and_version_type_minor_must_increment_minor_and_set_patch_0(self):
        actual = generate_version(version='1.2.3', version_type='minor')
        self.assertEqual(actual, '1.3.0')

    def test_non_rc_version_and_version_type_major_must_increment_major_and_set_minor_and_patch_0(self):
        actual = generate_version(version='1.2.3', version_type='major')
        self.assertEqual(actual, '2.0.0')

    def test_rc_version_and_version_type_rc_must_increment_rc(self):
        actual = generate_version(version='1.2.3-rc.3', version_type='rc')
        self.assertEqual(actual, '1.2.3-rc.4')

    def test_rc_version_and_version_type_patch_must_increment_patch_and_remove_rc(self):
        actual = generate_version(version='1.2.3-rc.3', version_type='patch')
        self.assertEqual(actual, '1.2.4')

    def test_rc_version_and_version_type_minor_must_increment_minor_and_set_patch_0_and_remove_rc(self):
        actual = generate_version(version='1.2.3-rc.3', version_type='minor')
        self.assertEqual(actual, '1.3.0')

    def test_rc_version_and_version_type_major_must_increment_major_and_set_minor_and_patch_0_and_remove_rc(self):
        actual = generate_version(version='1.2.3-rc.3', version_type='major')
        self.assertEqual(actual, '2.0.0')


if __name__ == '__main__':
    unittest.main()
