import json
from unittest import mock

import pytest

from gruhoedb.credentials import GoogleDocsCredentials

ENV_TO_KEY = {
    'GOOGLE_SERVICE_ACCOUNT_EMAIL': 'client_email',
    'GOOGLE_SERVICE_ACCOUNT_CLIENT_ID': 'client_id',
    'GOOGLE_SERVICE_ACCOUNT_KEY': 'private_key',
    'GOOGLE_SERVICE_ACCOUNT_KEY_ID': 'private_key_id',
    'GOOGLE_SERVICE_ACCOUNT_PROJECT_ID': 'project_id',
    'GOOGLE_SERVICE_ACCOUNT_TOKEN_URI': 'token_uri',
}


@pytest.fixture
def from_service_account_info():
    with mock.patch('gruhoedb.credentials.service_account.Credentials.from_service_account_info') as patched:
        yield patched


def test_from_file_builds_credentials_from_the_json_content(tmp_path, from_service_account_info):
    info = {'client_email': 'bot@example.com', 'private_key': 'secret'}
    path = tmp_path / 'service-account.json'
    path.write_text(json.dumps(info))

    result = GoogleDocsCredentials.from_file(path)

    from_service_account_info.assert_called_once_with(info)
    assert result.credentials is from_service_account_info.return_value


def test_from_envvars_builds_credentials_from_the_environment(monkeypatch, from_service_account_info):
    for envvar, key in ENV_TO_KEY.items():
        monkeypatch.setenv(envvar, f'value-of-{key}')
    monkeypatch.setenv('GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL', 'client-email-override')

    result = GoogleDocsCredentials.from_envvars()

    # client_email is listed twice; the later GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL wins.
    expected = {key: f'value-of-{key}' for key in ENV_TO_KEY.values()}
    expected['client_email'] = 'client-email-override'
    from_service_account_info.assert_called_once_with(expected)
    assert result.credentials is from_service_account_info.return_value
