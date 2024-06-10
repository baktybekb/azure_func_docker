from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    ldap_url: str
    manager_dn: str
    manager_password: str
    ldap_search_base: str
    group_patterns: str

    class Config:
        env_file = '../.env'

    @property
    def group_patterns_list(self) -> List[str]:
        return json.loads(self.group_patterns)
