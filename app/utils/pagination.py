from dataclasses import dataclass

from fastapi import Query, Request


@dataclass
class PaginationParams:
    limit: int
    offset: int


def get_pagination(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset)


def build_pagination_urls(
    request: Request,
    count: int,
    limit: int,
    offset: int,
) -> tuple[str | None, str | None]:
    next_url = None
    if offset + limit < count:
        next_url = str(request.url.include_query_params(limit=limit, offset=offset + limit))

    previous_url = None
    if offset > 0:
        prev_offset = max(offset - limit, 0)
        previous_url = str(request.url.include_query_params(limit=limit, offset=prev_offset))

    return next_url, previous_url
