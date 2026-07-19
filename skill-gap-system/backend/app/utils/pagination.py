"""
Simple offset-based pagination helper shared by list endpoints.
"""
from typing import Any

from fastapi import Query
from sqlalchemy.orm import Query as SAQuery


class Pagination:
    def __init__(self, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def paginate(query: SAQuery, pagination: Pagination) -> dict[str, Any]:
    total = query.count()
    items = query.offset(pagination.offset).limit(pagination.page_size).all()
    return {
        "items": items,
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "total_pages": (total + pagination.page_size - 1) // pagination.page_size if pagination.page_size else 0,
    }
