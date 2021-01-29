import pytest

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

# https://blog.jerrycodes.com/no-http-requests/
@pytest.fixture(autouse=True)
def no_http_requests(monkeypatch):
    def urlopen_mock(self, method, url, *args, **kwargs):
        raise RuntimeError(
            f"The test was about to {method} {self.scheme}://{self.host}{url}"
        )

    monkeypatch.setattr(
        "urllib3.connectionpool.HTTPConnectionPool.urlopen", urlopen_mock
    )
