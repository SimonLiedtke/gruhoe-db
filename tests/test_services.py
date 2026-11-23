from unittest import mock

from gruhoedb.models import Pick
from gruhoedb.services import SyncService

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
