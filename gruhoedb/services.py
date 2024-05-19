import os
from functools import cached_property

from gruhoedb.credentials import GoogleDocsCredentials
from gruhoedb.models import Pick
from gruhoedb.repos import PickRepository, GoogleDocsRepo


class SyncService:
    def __init__(self, pick_repo: PickRepository, gdoc_repos: list[GoogleDocsRepo]) -> None:
        self.pick_repo = pick_repo
        self.gdoc_repos = gdoc_repos

    def sync(self) -> None:
        self.pick_repo.add_many(self.to_be_added)

    @cached_property
    def to_be_added(self) -> list[Pick]:
        def inner():
            for doc in self.gdoc_repos:
                for pick in doc:
                    if pick is not None and pick not in self.pick_repo:
                        yield pick

        return list(inner())


class SyncServiceFactory:
    @staticmethod
    def create(locale: str):
        documents = os.environ.get('GOOGLE_DOCUMENT_IDS').split(';')
        creds = GoogleDocsCredentials.from_envvars()
        gdoc_repos = map(lambda doc: GoogleDocsRepo(creds, doc, locale), documents)
        pick_repo = PickRepository(os.environ.get('DB_CONNECTION'))

        return SyncService(pick_repo, gdoc_repos)
