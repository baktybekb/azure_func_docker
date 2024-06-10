import unittest
from unittest.mock import patch
from ldap3 import SUBTREE

from azure_function.services import LDAPService, LDAPApplication


class TestLDAPService(unittest.TestCase):
    """
    Unit tests for LDAPService class.
    """
    target = 'azure_function.services.Connection'

    @patch(target, autospec=True)
    def test_search_groups(self, MockConnection):
        """
        Test searching for groups in the LDAP directory.
        """
        mock_connection = MockConnection.return_value
        service = LDAPService(mock_connection)
        mock_connection.entries = ['entry1', 'entry2']

        result = service.search_groups('base_dn', ['group1', 'group2'])
        self.assertEqual(result, ['entry1', 'entry2'])
        mock_connection.search.assert_called_once_with(
            'base_dn',
            '(|(cn=group1)(cn=group2))',
            search_scope=SUBTREE,
            attributes=['member']
        )

    @patch(target, autospec=True)
    def test_search_groups_no_results(self, MockConnection):
        """
        Test searching for groups with no results.
        """
        mock_connection = MockConnection.return_value
        mock_connection.entries = []
        service = LDAPService(mock_connection)

        result = service.search_groups('base_dn', ['group1', 'group2'])
        self.assertEqual(result, [])
        mock_connection.search.assert_called_once_with(
            'base_dn',
            '(|(cn=group1)(cn=group2))',
            search_scope=SUBTREE,
            attributes=['member']
        )

    @patch(target, autospec=True)
    def test_search_groups_exception(self, MockConnection):
        """
        Test searching for groups with an exception raised.
        """
        mock_connection = MockConnection.return_value
        mock_connection.search.side_effect = Exception("LDAP search failed")
        service = LDAPService(mock_connection)

        with self.assertRaises(Exception) as context:
            service.search_groups('base_dn', ['group1', 'group2'])
        self.assertTrue('LDAP search failed' in str(context.exception))

    @patch(target, autospec=True)
    def test_search_users(self, MockConnection):
        """
        Test searching for users in the LDAP directory.
        """
        mock_connection = MockConnection.return_value
        service = LDAPService(mock_connection)
        mock_connection.entries = ['user1', 'user2']

        # Test for disabled_only=False
        result = service.search_users('base_dn', {'dn1', 'dn2'}, disabled_only=False)
        self.assertEqual(result, ['user1', 'user2'])
        args, kwargs = mock_connection.search.call_args
        self.assertEqual(args[0], 'base_dn')
        self.assertIn('(distinguishedName=dn1)', args[1])
        self.assertIn('(distinguishedName=dn2)', args[1])
        self.assertIn('(!(userAccountControl:1.2.840.113556.1.4.803:=2))', args[1])
        self.assertEqual(kwargs['search_scope'], SUBTREE)
        self.assertEqual(kwargs['attributes'], ['*'])

        # Reset mock for the next call
        mock_connection.reset_mock()

        # Test for disabled_only=True
        result = service.search_users('base_dn', {'dn1', 'dn2'}, disabled_only=True)
        self.assertEqual(result, ['user1', 'user2'])
        args, kwargs = mock_connection.search.call_args
        self.assertEqual(args[0], 'base_dn')
        self.assertIn('(distinguishedName=dn1)', args[1])
        self.assertIn('(distinguishedName=dn2)', args[1])
        self.assertIn('(userAccountControl:1.2.840.113556.1.4.803:=2)', args[1])
        self.assertEqual(kwargs['search_scope'], SUBTREE)
        self.assertEqual(kwargs['attributes'], ['*'])

    @patch(target, autospec=True)
    def test_search_users_no_results(self, MockConnection):
        """
        Test searching for users with no results.
        """
        mock_connection = MockConnection.return_value
        mock_connection.entries = []
        service = LDAPService(mock_connection)

        result = service.search_users('base_dn', {'dn1', 'dn2'})
        self.assertEqual(result, [])
        args, kwargs = mock_connection.search.call_args
        self.assertEqual(args[0], 'base_dn')
        self.assertIn('(distinguishedName=dn1)', args[1])
        self.assertIn('(distinguishedName=dn2)', args[1])
        self.assertIn('(!(userAccountControl:1.2.840.113556.1.4.803:=2))', args[1])
        self.assertEqual(kwargs['search_scope'], SUBTREE)
        self.assertEqual(kwargs['attributes'], ['*'])

    @patch(target, autospec=True)
    def test_fetch_user_dns_by_groups(self, MockConnection):
        """
        Test fetching user DNs by group patterns.
        """
        mock_connection = MockConnection.return_value
        service = LDAPService(mock_connection)
        mock_connection.entries = [
            {'member': ['user1', 'user2', 'user3']},
            {'member': ['user1', 'user2', 'user4']},
        ]

        result = service.fetch_user_dns_by_groups('base_dn', ['group1'])
        self.assertEqual(result, {'user1', 'user2', 'user3', 'user4'})
        mock_connection.search.assert_called_once_with(
            'base_dn',
            '(|(cn=group1))',
            search_scope=SUBTREE,
            attributes=['member']
        )


class TestLDAPApplication(unittest.TestCase):
    """
    Unit tests for LDAPApplication class.
    """
    target = 'azure_function.services.LDAPService'

    @patch(target, autospec=True)
    def test_run(self, MockLDAPService):
        """
        Test running the LDAP application.
        """
        mock_service = MockLDAPService.return_value
        mock_service.fetch_user_dns_by_groups.return_value = {'dn1', 'dn2'}
        mock_service.search_users.side_effect = [
            ['active_user1', 'active_user2'],
            ['disabled_user1']
        ]

        app = LDAPApplication(mock_service)
        app.run('base_dn', ['group1', 'group2'])

        mock_service.fetch_user_dns_by_groups.assert_called_once_with('base_dn', ['group1', 'group2'])
        mock_service.search_users.assert_any_call('base_dn', {'dn1', 'dn2'})
        mock_service.search_users.assert_any_call('base_dn', {'dn1', 'dn2'}, disabled_only=True)
