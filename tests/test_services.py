from unittest import mock

from gruhoedb.models import Pick
from gruhoedb.services import SyncService, SyncServiceFactory

FIRST = Pick(2024, 1, 1, 'First Artist', 'First Album')
SECOND = Pick(2024, 1, 2, 'Second Artist', 'Second Album')


def test_to_be_added_collects_picks_from_all_documents_and_drops_none():
    service = SyncService(mock.Mock(), [iter([None, FIRST, None]), iter([SECOND])])
    assert service.to_be_added == [FIRST, SECOND]


def test_sync_writes_the_new_picks_to_the_repository():
    pick_repo = mock.Mock()
    service = SyncService(pick_repo, [iter([FIRST, SECOND])])
    service.sync()
    pick_repo.add_many.assert_called_once_with([FIRST, SECOND])


def test_factory_wires_documents_and_repository_from_the_environment(monkeypatch):
    monkeypatch.setenv('GOOGLE_DOCUMENT_IDS', 'doc-1;doc-2')
    monkeypatch.setenv('DB_CONNECTION', 'postgresql://example')
    monkeypatch.setenv('DB_NAME', 'gruhoedb')

    with mock.patch('gruhoedb.services.GoogleDocsCredentials') as credentials, \
            mock.patch('gruhoedb.services.GoogleDocsRepo') as docs_repo, \
            mock.patch('gruhoedb.services.PickRepository') as pick_repository:
        service = SyncServiceFactory.create('de')
        gdoc_repos = list(service.gdoc_repos)

    creds = credentials.from_envvars.return_value
    assert docs_repo.call_args_list == [mock.call(creds, 'doc-1', 'de'), mock.call(creds, 'doc-2', 'de')]
    assert gdoc_repos == [docs_repo.return_value, docs_repo.return_value]
    pick_repository.assert_called_once_with('postgresql://example', 'gruhoedb')
    assert service.pick_repo is pick_repository.return_value
