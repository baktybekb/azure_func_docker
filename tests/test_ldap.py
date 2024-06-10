import pytest
from unittest.mock import patch
from ldap3 import SUBTREE

from azure_function.services import LDAPService, LDAPApplication


@pytest.fixture
def mock_connection():
    with patch('azure_function.services.Connection', autospec=True) as MockConnection:
        yield MockConnection.return_value


def test_search_groups(mock_connection):
    """
    Test searching for groups in the LDAP directory.
    """
    service = LDAPService(mock_connection)
    mock_connection.entries = ['entry1', 'entry2']

    result = service.search_groups('base_dn', ['group1', 'group2'])
    assert result == ['entry1', 'entry2']
    mock_connection.search.assert_called_once_with(
        'base_dn',
        '(|(cn=group1)(cn=group2))',
        search_scope=SUBTREE,
        attributes=['member']
    )


def test_search_groups_no_results(mock_connection):
    """
    Test searching for groups with no results.
    """
    mock_connection.entries = []
    service = LDAPService(mock_connection)

    result = service.search_groups('base_dn', ['group1', 'group2'])
    assert result == []
    mock_connection.search.assert_called_once_with(
        'base_dn',
        '(|(cn=group1)(cn=group2))',
        search_scope=SUBTREE,
        attributes=['member']
    )


def test_search_groups_exception(mock_connection):
    """
    Test searching for groups with an exception raised.
    """
    mock_connection.search.side_effect = Exception("LDAP search failed")
    service = LDAPService(mock_connection)

    with pytest.raises(Exception) as exc_info:
        service.search_groups('base_dn', ['group1', 'group2'])
    assert 'LDAP search failed' in str(exc_info.value)


def test_search_users(mock_connection):
    """
    Test searching for users in the LDAP directory.
    """
    service = LDAPService(mock_connection)
    mock_connection.entries = ['user1', 'user2']

    # Test for disabled_only=False
    result = service.search_users('base_dn', {'dn1', 'dn2'}, disabled_only=False)
    assert result == ['user1', 'user2']
    args, kwargs = mock_connection.search.call_args
    assert args[0] == 'base_dn'
    assert '(distinguishedName=dn1)' in args[1]
    assert '(distinguishedName=dn2)' in args[1]
    assert '(!(userAccountControl:1.2.840.113556.1.4.803:=2))' in args[1]
    assert kwargs['search_scope'] == SUBTREE
    assert kwargs['attributes'] == ['*']

    # Reset mock for the next call
    mock_connection.reset_mock()

    # Test for disabled_only=True
    result = service.search_users('base_dn', {'dn1', 'dn2'}, disabled_only=True)
    assert result == ['user1', 'user2']
    args, kwargs = mock_connection.search.call_args
    assert args[0] == 'base_dn'
    assert '(distinguishedName=dn1)' in args[1]
    assert '(distinguishedName=dn2)' in args[1]
    assert '(userAccountControl:1.2.840.113556.1.4.803:=2)' in args[1]
    assert kwargs['search_scope'] == SUBTREE
    assert kwargs['attributes'] == ['*']


def test_search_users_no_results(mock_connection):
    """
    Test searching for users with no results.
    """
    mock_connection.entries = []
    service = LDAPService(mock_connection)

    result = service.search_users('base_dn', {'dn1', 'dn2'})
    assert result == []
    args, kwargs = mock_connection.search.call_args
    assert args[0] == 'base_dn'
    assert '(distinguishedName=dn1)' in args[1]
    assert '(distinguishedName=dn2)' in args[1]
    assert '(!(userAccountControl:1.2.840.113556.1.4.803:=2))' in args[1]
    assert kwargs['search_scope'] == SUBTREE
    assert kwargs['attributes'] == ['*']


def test_fetch_user_dns_by_groups(mock_connection):
    """
    Test fetching user DNs by group patterns.
    """
    service = LDAPService(mock_connection)
    mock_connection.entries = [
        {'member': ['user1', 'user2', 'user3']},
        {'member': ['user1', 'user2', 'user4']},
    ]

    result = service.fetch_user_dns_by_groups('base_dn', ['group1'])
    assert result == {'user1', 'user2', 'user3', 'user4'}
    mock_connection.search.assert_called_once_with(
        'base_dn',
        '(|(cn=group1))',
        search_scope=SUBTREE,
        attributes=['member']
    )


@pytest.fixture
def mock_ldap_service():
    with patch('azure_function.services.LDAPService', autospec=True) as MockLDAPService:
        yield MockLDAPService.return_value


def test_run(mock_ldap_service):
    """
    Test running the LDAP application.
    """
    mock_ldap_service.fetch_user_dns_by_groups.return_value = {'dn1', 'dn2'}
    mock_ldap_service.search_users.side_effect = [
        ['active_user1', 'active_user2'],
        ['disabled_user1']
    ]

    app = LDAPApplication(mock_ldap_service)
    app.run('base_dn', ['group1', 'group2'])

    mock_ldap_service.fetch_user_dns_by_groups.assert_called_once_with('base_dn', ['group1', 'group2'])
    mock_ldap_service.search_users.assert_any_call('base_dn', {'dn1', 'dn2'})
    mock_ldap_service.search_users.assert_any_call('base_dn', {'dn1', 'dn2'}, disabled_only=True)
