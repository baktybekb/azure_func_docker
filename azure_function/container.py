from dependency_injector import containers, providers
from azure_function.config import Settings
from azure_function.services import LDAPConnection, LDAPService, LDAPApplication


class Container(containers.DeclarativeContainer):
    """
    Dependency injection container for the LDAP application.
    """
    config = providers.Singleton(Settings)

    ldap_connection = providers.Resource(
        LDAPConnection,
        ldap_url=config.provided.ldap_url,
        manager_dn=config.provided.manager_dn,
        manager_password=config.provided.manager_password,
    )

    ldap_service = providers.Factory(
        LDAPService,
        connection=ldap_connection
    )

    ldap_application = providers.Factory(
        LDAPApplication,
        ldap_service=ldap_service
    )
