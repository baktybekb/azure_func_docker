import logging
from ldap3 import Server, Connection, Tls, ALL, SUBTREE
import ssl
from typing import List, Set, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LDAPConnection:
    """
    A context manager for LDAP connection.

    Attributes:
        ldap_url (str): URL of the LDAP server.
        manager_dn (str): Distinguished Name of the manager.
        manager_password (str): Password for the manager DN.
        conn (Optional[Connection]): LDAP connection object.
    """

    def __init__(self, ldap_url: str, manager_dn: str, manager_password: str):
        """
        Initializes the LDAPConnection context manager.

        Args:
            ldap_url (str): URL of the LDAP server.
            manager_dn (str): Distinguished Name of the manager.
            manager_password (str): Password for the manager DN.
        """
        self.ldap_url = ldap_url
        self.manager_dn = manager_dn
        self.manager_password = manager_password
        self.conn: Optional[Connection] = None

    def __enter__(self) -> Connection:
        """
        Establishes the LDAP connection on entering the context.

        Returns:
            Connection: The LDAP connection object.
        """
        tls = Tls(validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1_2)
        self.conn = Connection(
            Server(self.ldap_url, use_ssl=True, tls=tls, get_info=ALL),
            user=self.manager_dn, password=self.manager_password, auto_bind=True
        )
        logger.info("Connected to the LDAP server.")
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Closes the LDAP connection on exiting the context.
        """
        if self.conn:
            self.conn.unbind()
            logger.info("Disconnected from the LDAP server.")


class LDAPService:
    """
    A service for interacting with the LDAP server.

    Attributes:
        connection (Connection): LDAP connection object.
    """

    def __init__(self, connection: Connection):
        """
        Initializes the LDAPService.

        Args:
            connection (Connection): LDAP connection object.
        """
        self.connection = connection

    def search_groups(self, search_base: str, group_patterns: List[str]) -> List:
        """
        Searches for groups in the LDAP directory.

        Args:
            search_base (str): Base DN to search within.
            group_patterns (List[str]): List of group name patterns to search for.

        Returns:
            List: List of LDAP entries matching the group patterns.
        """
        group_filter = "(|" + "".join([f"(cn={pattern})" for pattern in group_patterns]) + ")"
        self.connection.search(search_base, group_filter, search_scope=SUBTREE, attributes=['member'])
        return self.connection.entries

    def search_users(self, search_base: str, user_dns: Set[str], disabled_only: bool = False) -> List:
        """
        Searches for users in the LDAP directory.

        Args:
            search_base (str): Base DN to search within.
            user_dns (Set[str]): Set of user distinguished names to search for.
            disabled_only (bool, optional): Whether to search for disabled users only. Defaults to False.

        Returns:
            List: List of LDAP entries matching the user DNs.
        """
        if not user_dns:
            return []

        user_filter = "(|" + "".join([f"(distinguishedName={user_dn})" for user_dn in user_dns]) + ")"
        if disabled_only:
            user_filter = f"(&{user_filter}(userAccountControl:1.2.840.113556.1.4.803:=2))"
        else:
            user_filter = f"(&{user_filter}(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"

        self.connection.search(search_base, user_filter, search_scope=SUBTREE, attributes=['*'])
        return self.connection.entries

    def fetch_user_dns_by_groups(self, search_base: str, group_patterns: List[str]) -> Set[str]:
        """
        Fetches user distinguished names by group patterns.

        Args:
            search_base (str): Base DN to search within.
            group_patterns (List[str]): List of group name patterns to search for.

        Returns:
            Set[str]: Set of user distinguished names found in the matching groups.
        """
        groups = self.search_groups(search_base, group_patterns)
        if not groups:
            logger.info("No groups found with the specified patterns.")
            return set()

        user_dns: Set[str] = set()
        for group in groups:
            user_dns.update(group['member'])

        if not user_dns:
            logger.info("No members found in the matching groups.")
            return set()

        return user_dns


class LDAPApplication:
    """
    Main application for running LDAP queries.

    Attributes:
        ldap_service (LDAPService): Instance of LDAPService.
    """

    def __init__(self, ldap_service: LDAPService):
        """
        Initializes the LDAPApplication.

        Args:
            ldap_service (LDAPService): Instance of LDAPService.
        """
        self.ldap_service = ldap_service

    def run(self, search_base: str, group_patterns: List[str]):
        """
        Runs the LDAP query application.

        Args:
            search_base (str): Base DN to search within.
            group_patterns (List[str]): List of group name patterns to search for.
        """
        logger.info("Fetching user DNs from groups...")
        user_dns = self.ldap_service.fetch_user_dns_by_groups(search_base, group_patterns)

        logger.info("Fetching users...")
        active_users = self.ldap_service.search_users(search_base, user_dns)
        if active_users:
            pass  # sending disabled users to message queue
        else:
            logger.info("No user entries found.")

        logger.info("Fetching disabled users...")
        disabled_users = self.ldap_service.search_users(search_base, user_dns, disabled_only=True)
        if disabled_users:
            pass  # sending disabled users to message queue
        else:
            logger.info("No disabled user entries found.")

        logger.info("LDAP Query Completed Successfully.")
