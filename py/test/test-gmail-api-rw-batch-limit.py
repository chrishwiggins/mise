#!/usr/bin/env python3
"""Tests for gmail-api-rw do_list batch chunking (2026-08-14 fixit).

Gmail's /batch endpoint rejects more than 100 inner requests with HTTP 400
("Inner request count exceeds the limit"). Listing 110 messages (m ... pp11)
crashed do_list, which put one messages.get per row into a single batch.
The fix chunks the gets into successive batches of at most 100.

No credentials, no network: do_list is driven with a stub service whose
batch object enforces the real 100-request limit.
Run with the venv python (googleapiclient must import):
  /Users/wiggins/mise/py/.venv/bin/python3 test-gmail-api-rw-batch-limit.py
or via pytest.
"""
import contextlib
import importlib.util
import io
import json
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "gmail-api-rw"

spec = importlib.util.spec_from_file_location(
    "gmail_api_rw", SCRIPT_PATH,
    loader=SourceFileLoader("gmail_api_rw", str(SCRIPT_PATH)),
)
gm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gm)


class FakeBatchLimitError(Exception):
    """Stands in for the HttpError 400 the real /batch endpoint returns."""


class FakeGetRequest:
    def __init__(self, msg_id):
        self.msg_id = msg_id

    def execute(self):
        return _meta_response(self.msg_id)


def _meta_response(msg_id):
    return {
        "id": msg_id,
        "threadId": "t-" + msg_id,
        "labelIds": [],
        "payload": {"headers": [
            {"name": "From", "value": "Sender <sender@example.edu>"},
            {"name": "Subject", "value": "subject " + msg_id},
            {"name": "Date", "value": "Mon, 13 Feb 2023 09:42:00 -0500"},
        ]},
    }


class FakeBatch:
    """Enforces the real Gmail limit: >100 inner requests -> error."""

    def __init__(self, log):
        self.log = log
        self.entries = []

    def add(self, request, callback=None):
        self.entries.append((request, callback))

    def execute(self):
        self.log.append(len(self.entries))
        if len(self.entries) > 100:
            raise FakeBatchLimitError(
                f"Inner request count exceeds the limit. "
                f"Received: {len(self.entries)}, Limit: 100")
        for i, (request, callback) in enumerate(self.entries):
            callback(str(i), _meta_response(request.msg_id), None)


class FakeService:
    def __init__(self, n_messages, batch_log):
        self.n = n_messages
        self.batch_log = batch_log

    def users(self):
        return self

    def messages(self):
        return self

    def list(self, **kwargs):
        stubs = [{"id": f"m{i:03d}"} for i in range(self.n)]

        class _Req:
            def execute(_self):
                return {"messages": stubs}
        return _Req()

    def get(self, userId=None, id=None, format=None, metadataHeaders=None):
        return FakeGetRequest(id)

    def new_batch_http_request(self):
        return FakeBatch(self.batch_log)


def _run_do_list(n_messages):
    """Run do_list over n stub messages; return (json rows, batch sizes)."""
    batch_log = []
    service = FakeService(n_messages, batch_log)
    saved_cache = gm._cache_message_ids
    saved_retry = gm._retry_api_call
    gm._cache_message_ids = lambda *a, **k: None
    gm._retry_api_call = lambda fn, *a, **k: fn()  # avoid google_auth import
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            gm.do_list(service, n_messages, "subject:test",
                       json_output=True, no_cache=True)
    finally:
        gm._cache_message_ids = saved_cache
        gm._retry_api_call = saved_retry
    return json.loads(out.getvalue()), batch_log


def test_110_messages_chunked_under_batch_limit():
    """The pp11 crash: 110 rows must split into batches of <=100."""
    rows, batch_log = _run_do_list(110)
    assert max(batch_log) <= 100, f"batch exceeded limit: {batch_log}"
    assert sum(batch_log) == 110, f"requests lost in chunking: {batch_log}"
    assert len(rows) == 110
    assert not any(r.get("error") for r in rows), "fetch errors in output"
    assert [r["id"] for r in rows] == [f"m{i:03d}" for i in range(110)], \
        "chunking broke row order"


def test_100_messages_single_batch():
    """At the limit exactly, one batch suffices."""
    rows, batch_log = _run_do_list(100)
    assert batch_log == [100], f"unexpected batching: {batch_log}"
    assert len(rows) == 100


def test_small_listing_unaffected():
    rows, batch_log = _run_do_list(7)
    assert batch_log == [7]
    assert len(rows) == 7


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok   {name}")
            except (AssertionError, FakeBatchLimitError) as e:
                failures += 1
                print(f"FAIL {name}: {e}")
    sys.exit(1 if failures else 0)
