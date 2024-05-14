import json
import os

from google.oauth2 import service_account


class GoogleDocsCredentials:
    def __init__(self, credentials) -> None:
        self.credentials = credentials

    @classmethod
    def from_file(cls, filename):
        with open(filename) as f:
            service_account_info = json.load(f)
            credentials = service_account.Credentials.from_service_account_info(service_account_info)
        return cls(credentials)

    @classmethod
    def from_envvars(cls):
        keys = [
            ('client_email', 'GOOGLE_SERVICE_ACCOUNT_EMAIL'),
            ('client_id', 'GOOGLE_SERVICE_ACCOUNT_CLIENT_ID'),
            ('private_key', 'GOOGLE_SERVICE_ACCOUNT_KEY'),
            ('private_key_id', 'GOOGLE_SERVICE_ACCOUNT_KEY_ID'),
            ('project_id', 'GOOGLE_SERVICE_ACCOUNT_PROJECT_ID'),
            ('client_email', 'GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL'),
            ('token_uri', 'GOOGLE_SERVICE_ACCOUNT_TOKEN_URI'),
        ]
        service_account_info = {}
        for (key, envvar) in keys:
            service_account_info[key] = os.environ.get(envvar)
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        return cls(credentials)
