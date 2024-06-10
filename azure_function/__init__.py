from azure_function.container import Container
import logging
import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    logging.info('Hello world!')

    container = Container()
    with container.ldap_connection() as conn:
        ldap_service = container.ldap_service(connection=conn)
        app = container.ldap_application(ldap_service=ldap_service)
        config = container.config()
        app.run(config.ldap_search_base, config.group_patterns_list)
