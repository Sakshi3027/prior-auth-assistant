"""
Temporary in-memory store for processed prior auth requests.

This exists so the API works end to end before we introduce Postgres.
It's deliberately a drop-in shape: the same save/list/get interface a
real database repository will expose, so swapping it out later is a
one-file change with no route rewrites.
"""
from api.schemas import PriorAuthResult

_requests: list[PriorAuthResult] = []


def save(result: PriorAuthResult) -> None:
    _requests.append(result)


def list_all() -> list[PriorAuthResult]:
    return list(reversed(_requests))  # newest first


def get(request_id: str) -> PriorAuthResult | None:
    return next((r for r in _requests if r.id == request_id), None)