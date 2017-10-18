#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from ci_helper import clean_content
from tests.unit import BaseTest


class TestCleanContent(BaseTest):
    """This class tests the clean_content method"""

    def test_empty_text_must_return_empty_list(self):
        actual = clean_content('')
        self.assertEqual(actual, [])

    def test_one_item_in_text_must_return_list_with_item(self):
        actual = clean_content('  it em  ')
        self.assertEqual(actual, ['it em'])

    def test_one_item_starts_with_star_in_text_must_return_list_with_item(self):
        actual = clean_content('  *  it em   ')
        self.assertEqual(actual, ['it em'])

    def test_one_item_starts_with_hyphen_in_text_must_return_list_with_item(self):
        actual = clean_content('  -  it em   ')
        self.assertEqual(actual, ['it em'])

    def test_one_item_starts_with_stars_and_hyphens_in_text_must_return_list_with_item(self):
        actual = clean_content('  * -  it em   ')
        self.assertEqual(actual, ['it em'])

    def test_one_item_starts_with_stars_in_text_must_return_list_with_item(self):
        actual = clean_content('  ** * *  it em   ')
        self.assertEqual(actual, ['it em'])

    def test_one_item_starts_with_hyphens_in_text_must_return_list_with_item(self):
        actual = clean_content('  -- - -  it em   ')
        self.assertEqual(actual, ['it em'])

    def test_one_item_starts_with_user_ref_text_must_return_empty_list(self):
        actual = clean_content('  -[]@user.us-er   ')
        self.assertEqual(actual, [])

    def test_one_item_starts_with_user_ref_checked_text_must_return_empty_list(self):
        actual = clean_content('  -  [x]   @  user.us-er   ')
        self.assertEqual(actual, [])

    def test_multiple_items_must_return_list_with_valid_changes(self):
        actual = clean_content('  - item1\n\n\n  - [X] @user  \n* item2   \n item3\n\n  \n- [ ] @user-test  \n')
        self.assertEqual(actual, ['item1', 'item2', 'item3'])


if __name__ == '__main__':
    unittest.main()
