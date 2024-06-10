from azure_function.container import Container
import logging
import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    logging.info('Bahaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    logging.info('=' * 20)

    container = Container()
    with container.ldap_connection() as conn:
        ldap_service = container.ldap_service(connection=conn)
        app = container.ldap_application(ldap_service=ldap_service)
        config = container.config()
        app.run(config.ldap_search_base, config.group_patterns_list)

# if __name__ == '__main__':
#     container = Container()
#     with container.ldap_connection() as conn:
#         ldap_service = container.ldap_service(connection=conn)
#         app = container.ldap_application(ldap_service=ldap_service)
#         config = container.config()
#         app.run(config.ldap_search_base, config.group_patterns_list)
