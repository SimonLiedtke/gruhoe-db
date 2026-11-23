from unittest import mock

import pytest

from gruhoedb import webserver

PASSWORD = 'correct horse'


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('ADMIN_PASSWORD', PASSWORD)
    return webserver.app.test_client()


@pytest.fixture
def sync_service():
    with mock.patch.object(webserver.SyncServiceFactory, 'create') as create:
        service = create.return_value
        service.to_be_added = [[2024, 1, 2, 'Artist', 'Album']]
        yield service


def login(client, password=PASSWORD):
    return client.post('/login', data={'password': password})


@pytest.mark.parametrize('method, url', [('get', '/newpicks'), ('post', '/sync')])
def test_protected_routes_require_login(client, sync_service, method, url):
    assert getattr(client, method)(url).status_code == 401
    sync_service.sync.assert_not_called()


@pytest.mark.parametrize('data', [
    {'password': 'wrong'},
    {'password': ''},
    {'password': 'ünïcödé'},
    {},
])
def test_login_rejects_bad_passwords(client, sync_service, data):
    assert client.post('/login', data=data).status_code == 401
    assert client.post('/sync').status_code == 401


def test_login_fails_closed_without_configured_password(client, sync_service, monkeypatch):
    monkeypatch.delenv('ADMIN_PASSWORD')
    assert login(client, password='').status_code == 401
    assert client.post('/sync').status_code == 401


def test_login_grants_access_to_protected_routes(client, sync_service):
    assert login(client).status_code == 200
    assert client.get('/newpicks').status_code == 200
    assert client.post('/sync').status_code == 200
    sync_service.sync.assert_called_once()


def test_login_is_bound_to_the_session(client, sync_service):
    login(client)
    other_client = webserver.app.test_client()
    assert other_client.post('/sync').status_code == 401


def test_session_cookie_is_httponly_and_samesite_lax(client):
    cookie = login(client).headers['Set-Cookie']
    assert 'HttpOnly' in cookie
    assert 'SameSite=Lax' in cookie
