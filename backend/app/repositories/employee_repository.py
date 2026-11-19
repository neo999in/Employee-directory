import re
from typing import List, Optional

from sqlalchemy import and_, func, literal, or_, text
from sqlalchemy.orm import Session

from app.models.employee import Employee

# Terms of at least this many characters go to the FULLTEXT index (InnoDB's
# default innodb_ft_min_token_size is 3, so shorter tokens are not indexed).
FULLTEXT_MIN_TERM_LENGTH = 3

_WORD = re.compile(r"\w+", re.UNICODE)


def split_terms(search: str) -> List[str]:
    """Split user input into plain word tokens.

    Dropping everything that is not a letter/digit/underscore also removes the
    MySQL boolean-mode operators (+ - < > ( ) ~ * " @), so input can't alter the query.
    """
    return _WORD.findall(search)


def _like_prefix(column, term: str):
    safe = term.replace("\\", "\\\\").replace("%", r"\%").replace("_", r"\_")
    return column.like(f"{safe}%", escape="\\")


class EmployeeRepository:
    """Database layer: the ONLY place that talks to the employees table."""

    def __init__(self, db: Session):
        self.db = db

    def _filter(self, query, search: str):
        terms = split_terms(search)
        if not terms:
            return query.filter(literal(False))  # only punctuation typed: nothing can match

        long_terms = [t for t in terms if len(t) >= FULLTEXT_MIN_TERM_LENGTH]
        short_terms = [t for t in terms if len(t) < FULLTEXT_MIN_TERM_LENGTH]
        conditions = []

        if long_terms:
            if self.db.get_bind().dialect.name == "mysql":
                # "+sharma* +eng*": every term must start a word in name or department.
                boolean_query = " ".join(f"+{t}*" for t in long_terms)
                conditions.append(
                    text("MATCH(employees.name, employees.department) AGAINST (:q IN BOOLEAN MODE)")
                    .bindparams(q=boolean_query)
                )
            else:
                # SQLite (tests only) has no FULLTEXT; emulate "term starts a word".
                for t in long_terms:
                    conditions.append(
                        or_(
                            _like_prefix(Employee.name, t),
                            Employee.name.contains(f" {t}", autoescape=True),
                            Employee.name.contains(f"-{t}", autoescape=True),
                            _like_prefix(Employee.department, t),
                            Employee.department.contains(f" {t}", autoescape=True),
                        )
                    )

        # 1-2 character terms ("HR"): indexed prefix match on the start of name / department.
        for t in short_terms:
            conditions.append(or_(_like_prefix(Employee.name, t), _like_prefix(Employee.department, t)))

        return query.filter(and_(*conditions))

    def search(self, search: Optional[str], limit: int, offset: int) -> List[Employee]:
        query = self.db.query(Employee)
        if search:
            query = self._filter(query, search)
        return query.order_by(Employee.name, Employee.id).offset(offset).limit(limit).all()

    def count(self, search: Optional[str]) -> int:
        query = self.db.query(func.count(Employee.id))
        if search:
            query = self._filter(query, search)
        return query.scalar()
